import logging
from datetime import timedelta, datetime

from fastapi import HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from fastapi.security.utils import get_authorization_scheme_param
from typing import Optional

from core.config import settings
from core.hashing import Hasher
from db.repository.users import UserRepository
from schemas.token import Token

class AuthHandlerService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
    
    def generate_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def authenticate_user(self, email: str, password: str) -> bool:
        user = self.user_repository.get_active_user_by_email(email=email)
        if not user:
            return False
        if not Hasher.verify_password(password, user.hashed_password):
            return False
        return user

    def create_access_token(self, email: str) -> str:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.generate_access_token(
            data={"email": email},
            expires_delta=access_token_expires
        )
        return access_token

    def login(self, response: Response, form_data: OAuth2PasswordRequestForm) -> Token:
        user = self.authenticate_user(form_data.email, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        access_token = self.create_access_token(user.email)
        response.set_cookie(
            key="access_token", value=f"Bearer {access_token}", httponly=True
        )
        return {"access_token": access_token, "token_type": "bearer"}

    def get_current_user_from_token(self, token: str):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            email: str = payload.get("email")
            logging.info(email)
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        user = self.user_repository.get_active_user_by_email(email=email)
        if user is None:
            raise credentials_exception
        return user
    
    def get_authenticated_user(self, token):
        _, param = get_authorization_scheme_param(
            token
        )
        return self.get_current_user_from_token(token=param)
