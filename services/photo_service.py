from sqlalchemy.orm import Session

from db.repository.reaction import (
    create_dislike,
    create_like,
    delete_reaction,
    fetch_reaction_by_user_id_and_photo_id
)
from db.repository.photo import fetch_photo_for_update
from db.models import Reaction
from db.models import User
from db.models import Photo

class PhotoService:
    def __init__(self, db: Session):
        self.db = db

    def toggle_like(self, user: User, photo_id: int):
        reaction: Reaction = fetch_reaction_by_user_id_and_photo_id(user.id, photo_id, self.db)
        photo: Photo = fetch_photo_for_update(photo_id, self.db)
        if reaction is None:
            reaction = create_like(user.id, photo_id, self.db)
            photo.like_count += 1
        elif reaction.liked == True:
            reaction.liked = False
            photo.like_count -= 1
            delete_reaction(reaction, self.db)
        else:
            reaction.liked = True
            photo.like_count += 1
            if reaction.disliked:
                reaction.disliked = False
                photo.dislike_count -= 1
        
        self.db.commit()

    
    def toggle_dislike(self, user: User, photo_id: int):
        reaction: Reaction = fetch_reaction_by_user_id_and_photo_id(user.id, photo_id, self.db)
        photo: Photo = fetch_photo_for_update(photo_id, self.db)
        if reaction is None:
            reaction = create_dislike(user.id, photo_id, self.db)
            photo.dislike_count += 1
        elif reaction.disliked == True:
            reaction.disliked = False
            photo.dislike_count -= 1
            delete_reaction(reaction, self.db)
        else:
            reaction.disliked = True
            photo.dislike_count += 1
            if reaction.liked:
                reaction.liked = False
                photo.like_count -= 1
        
        self.db.commit()
