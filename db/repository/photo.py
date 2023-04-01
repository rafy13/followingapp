from datetime import datetime, timedelta

import sqlalchemy
from sqlalchemy.orm import Session, selectinload

from db.models.photos import Photo, Gallery
from schemas.photos import CreatePhoto
from db.models import User, Follow, Reaction


def create_new_photo(photo: CreatePhoto, user: User, gallery: Gallery, db: Session):
    photo = Photo(
        filename=photo.filename,
        caption=photo.caption,
        gallery=gallery,
        owner=user
    )
    db.add(photo)
    db.commit()
    return photo

def fetch_photo_for_update(id: int, db: Session):
    return db.query(Photo) \
    .filter(Photo.id == id) \
    .with_for_update() \
    .first()

# User.followers.any(follower_id=current_user.id).label('followed_by_current_user')

def fetch_timeline_photos(user: User, db: Session):
    date_30_days_ago = datetime.utcnow() - timedelta(days=30)
    return db.query(
        Photo, 
        Photo.reactions.any(sqlalchemy.and_(Reaction.user_id==user.id, Reaction.liked==True)).label("has_liked"),
        Photo.reactions.any(sqlalchemy.and_(Reaction.user_id==user.id, Reaction.disliked==True)).label("has_disliked"),
    ) \
        .join(Follow, Follow.followed_id == Photo.owner_id) \
        .filter(sqlalchemy.or_(Follow.follower_id == user.id, Photo.owner_id == user.id)) \
        .filter(Photo.created_at >= date_30_days_ago) \
        .options(
            selectinload(Photo.owner),
            selectinload(Photo.gallery),
        ) \
        .order_by(Photo.created_at.desc()) \
        .all()

