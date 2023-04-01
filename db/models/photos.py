from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func

from db.models.base import Base


class Gallery(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner_id = Column(Integer, ForeignKey('user.id'))
    owner = relationship("db.models.users.User", back_populates="galleries")
    
    photos = relationship("db.models.photos.Photo", back_populates="gallery")

class Photo(Base):
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    caption = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    like_count = Column(Integer, default=0)
    dislike_count = Column(Integer, default=0)
    
    gallery_id = Column(Integer, ForeignKey('gallery.id'))
    gallery = relationship("Gallery", back_populates="photos")
    
    owner_id = Column(Integer, ForeignKey('user.id'))
    owner = relationship("db.models.users.User", back_populates="photos")

class Reaction(Base):
    id = Column(Integer, primary_key=True, index=True)
    photo_id = Column(Integer, ForeignKey("photo.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime, default=func.now())
    liked = Column(Boolean, default=False)
    disliked = Column(Boolean, default=False)

    photo = relationship("Photo", backref="reactions")
    user = relationship("db.models.users.User", backref="reactions")
