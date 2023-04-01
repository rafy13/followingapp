import os
import uuid
import shutil

from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError

from db.repository.reaction import ReactionRepository
from db.repository.photo import PhotoRepository
from db.repository.gallery import GalleryRepository
from db.models import Reaction
from db.models import User
from db.models import Photo
from schemas.photos import CreatePhoto
from webapp.photos.upload_photo_form import CreatePhotoForm

class PhotoService:
    def __init__(self, db: Session):
        self.db = db
        self.reaction_repo = ReactionRepository(db)
        self.photo_repo = PhotoRepository(db)
        self.gallery_repo = GalleryRepository(db)

    def toggle_like(self, user: User, photo_id: int):
        reaction: Reaction = self.reaction_repo.fetch_reaction_by_user_id_and_photo_id(user.id, photo_id)
        photo: Photo = self.photo_repo.get_photo_for_update(photo_id)
        if reaction is None:
            reaction = self.reaction_repo.create_like(user.id, photo_id)
            photo.like_count += 1
        elif reaction.liked == True:
            reaction.liked = False
            photo.like_count -= 1
            self.reaction_repo.delete(reaction)
        else:
            reaction.liked = True
            photo.like_count += 1
            if reaction.disliked:
                reaction.disliked = False
                photo.dislike_count -= 1
        
        self.db.commit()

    
    def toggle_dislike(self, user: User, photo_id: int):
        reaction: Reaction = self.reaction_repo.fetch_reaction_by_user_id_and_photo_id(user.id, photo_id)
        photo: Photo = self.photo_repo.get_photo_for_update(photo_id)
        if reaction is None:
            reaction = self.reaction_repo.create_dislike(user.id, photo_id)
            photo.dislike_count += 1
        elif reaction.disliked == True:
            reaction.disliked = False
            photo.dislike_count -= 1
            self.reaction_repo.delete(reaction)
        else:
            reaction.disliked = True
            photo.dislike_count += 1
            if reaction.liked:
                reaction.liked = False
                photo.like_count -= 1
        
        self.db.commit()

    def upload_photo(self, gallery_id: int, user: User, image_file, form: CreatePhotoForm):
        gallery = self.gallery_repo.get_galleries_by_user_id(
            id=gallery_id,
            user_id=user.id
        )
        if not gallery:
            raise HTTPException(status_code=404, detail="Gallery not found")
        
        file_name = str(uuid.uuid4())+image_file.filename
        if not file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            raise RequestValidationError("Upload a valid image file")
        
        file_path = f"static/uploads/{gallery_id}/{file_name}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
        create_photo_dto = CreatePhoto(filename = f"uploads/{gallery_id}/{file_name}", caption = form.caption)
        db_photo = self.photo_repo.create(
            photo=create_photo_dto,
            user=user,
            gallery=gallery
        )

        return db_photo, gallery 
