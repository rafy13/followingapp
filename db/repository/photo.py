from datetime import datetime, timedelta

import sqlalchemy
from sqlalchemy.orm import Session, selectinload

from db.models.photos import Photo, Gallery
from schemas.photos import CreatePhoto
from db.models import User, Follow, Reaction
from db.repository.base import BaseRepository


class PhotoRepository(BaseRepository[Gallery]):
    def __init__(self, db: Session):
        super().__init__(db, Photo)

    def create(self, photo: CreatePhoto, user: User, gallery: Gallery ) -> Photo:
        
        return super().create(Photo(
            filename=photo.filename,
            caption=photo.caption,
            gallery=gallery,
            owner=user))

    def get_timeline_photos(self, user: User):
        date_30_days_ago = datetime.utcnow() - timedelta(days=30)
        followed_users_ids = [user.id] + [follow.followed_id for follow in self.db.query(Follow).filter(Follow.follower_id == user.id)]
        return self.db.query(
            Photo, 
            Photo.reactions.any(sqlalchemy.and_(Reaction.user_id==user.id, Reaction.liked==True)).label("has_liked"),
            Photo.reactions.any(sqlalchemy.and_(Reaction.user_id==user.id, Reaction.disliked==True)).label("has_disliked"),
        ) \
        .filter(Photo.owner_id.in_(followed_users_ids)) \
        .filter(Photo.created_at >= date_30_days_ago) \
        .options(
            selectinload(Photo.owner),
            selectinload(Photo.gallery),
        ) \
        .order_by(Photo.created_at.desc()) \
        .all()
        # .outerjoin(Follow, Follow.followed_id == Photo.owner_id) \
        # .filter(sqlalchemy.or_(Follow.follower_id == user.id, Photo.owner_id == user.id)) \
    def get_photo_for_update(self, id: int):
        return self.db.query(Photo) \
            .filter(Photo.id == id) \
            .with_for_update() \
            .first()
