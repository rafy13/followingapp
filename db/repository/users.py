import uuid
from datetime import datetime, timedelta

import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy import func

from core.hashing import Hasher
from db.models.users import User, ActivationToken, Follow
from schemas.users import UserRegistration
from core.config import settings
from db.repository.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(db, User)
    
    def _get_distence_query(self, latitude, longitude):
        return func.ST_DistanceSphere(
            func.ST_MakePoint(func.cast(User.location_latitude, sqlalchemy.Float), func.cast( User.location_longitude, sqlalchemy.Float)),
            func.ST_MakePoint(func.cast(latitude, sqlalchemy.Float), func.cast(longitude, sqlalchemy.Float))
        )
    
    def create_user_activation_token(self):
        expires_at = datetime.utcnow() + timedelta(days=1)
        activation_token = ActivationToken(
            expires_at=expires_at,
            token = str(uuid.uuid4()))
        return activation_token
    
    def create(self, user: UserRegistration):
        user = User(
            name=user.name,
            email=user.email,
            hashed_password=Hasher.get_password_hash(user.password),
            location_latitude=user.location_latitude,
            location_longitude=user.location_longitude,
            date_of_birth=user.date_of_birth,
            gender=user.gender,
            activation_token = [self.create_user_activation_token()]
        )
        return super().create(user)

    def get_active_user_by_email(self, email: str):
        user = self.db.query(User) \
            .filter(User.email == email) \
            .filter(User.is_active == True) \
            .first()
        return user

    def get_active_user(self, id: str):
        user = self.db.query(User) \
            .filter(User.id == id) \
            .filter(User.is_active == True) \
            .first()
        return user

    def fetch_nearby_active_users(self, current_user: User):
        distance_query = self._get_distence_query(current_user.location_latitude, current_user.location_longitude)
        users =  self.db.query(
            User.id,
            User.name,
            User.profile_image,
            User.gender,
            func.date_part('year', func.age(User.date_of_birth)).label("age"),
            distance_query.label('distance'),
            User.followers.any(follower_id=current_user.id).label('followed_by_current_user')
        ) \
        .filter(User.is_active == True) \
        .filter(distance_query < settings.NEARBY_PLACE_MAX_DISTANCE) \
        .filter(User.id != current_user.id) \
        .all()
        
        return users

    def get_active_user_by_activation_token(self, token: str):
        return self.db.query(User) \
            .join(ActivationToken, ActivationToken.user_id == User.id) \
            .filter(ActivationToken.token == token) \
            .filter(ActivationToken.expires_at > datetime.now()) \
            .filter(ActivationToken.is_active == True) \
            .first()

    