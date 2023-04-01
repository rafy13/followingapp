from core.hashing import Hasher
from db.models.photos import Gallery
from schemas.photos import CreateGallery
from sqlalchemy.orm import Session

from db.models.users import User


def create_new_gallery(gallery: CreateGallery, user: User, db: Session):
    gallery = Gallery(
        name=gallery.name,
        owner=user
    )
    db.add(gallery)
    db.commit()
    db.refresh(gallery)
    return gallery

def retrieve_gallery(id: int, db: Session):
    return db.query(Gallery).filter(Gallery.id == id).first()

def retrive_gallery_by_user_id(id: int, user_id: int, db: Session):
    return db.query(Gallery) \
        .filter(Gallery.id == id) \
        .filter(Gallery.owner_id == user_id) \
        .first()