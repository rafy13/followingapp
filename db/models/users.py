import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.sql import func

from db.models.base import Base


class User(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    profile_image = Column(String(255))
    hashed_password =  Column(String, nullable=False)
    location_latitude = Column(Float)
    location_longitude = Column(Float)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    galleries = relationship("db.models.photos.Gallery", back_populates="owner")
    photos = relationship("db.models.photos.Photo", back_populates="owner")
    activation_token = relationship("ActivationToken", back_populates="user")


class Follow(Base):
    id = Column(Integer, primary_key=True)
    follower_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    follower = relationship("User", foreign_keys=[follower_id], backref="following")
    followed_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    followed = relationship("User", foreign_keys=[followed_id], backref="followers")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class ActivationToken(Base):
    id = Column(Integer, primary_key=True)
    token = Column(String(36), unique=True, nullable=False, default=str(uuid.uuid4()))
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship("User", back_populates="activation_token")

    @staticmethod
    def generate_activation_token(user: User):
        expires_at = datetime.utcnow() + timedelta(days=1)
        activation_token = ActivationToken(expires_at=expires_at, token = str(uuid.uuid4()), user=user)
        return activation_token