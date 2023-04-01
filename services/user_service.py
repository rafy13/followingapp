import uuid
import os
import shutil

from sqlalchemy.orm import Session
from fastapi.exceptions import RequestValidationError

from db.repository.follow import FollowRepository
from db.repository.users import UserRepository
from db.models import User

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.follow_repository = FollowRepository(db)
        self.user_repository = UserRepository(db)
    
    def upload_profile_image(self, user: User, profile_image):
        file_name = str(uuid.uuid4())+profile_image.filename
        if not file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            raise RequestValidationError("Upload a valid image file")
        file_path = f"static/profile_pictures/{user.id}/{file_name}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(profile_image.file, buffer)

        profile_image = f"profile_pictures/{user.id}/{file_name}"
        return self.user_repository.update(user, profile_image=profile_image)

    def check_is_follower(self, follower_id: int, followed_id: int) -> bool:
        return self.follow_repository.get_by_follower_id_followed_id(follower_id, followed_id) is not None
