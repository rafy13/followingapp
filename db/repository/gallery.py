from core.hashing import Hasher
from db.models.photos import Gallery
from schemas.photos import CreateGallery
from sqlalchemy.orm import Session

from db.models.users import User
from db.repository.base import BaseRepository

class GalleryRepository(BaseRepository[Gallery]):
    def __init__(self, db: Session):
        super().__init__(db, Gallery)

    def create(self, gallery: CreateGallery, user: User):
        gallery = Gallery(
            name=gallery.name,
            owner=user
        )
        return super().create(gallery)

    def get_galleries_by_user_id(self, id: int, user_id: int):
        return self.db.query(Gallery) \
            .filter(Gallery.id == id) \
            .filter(Gallery.owner_id == user_id) \
            .first()