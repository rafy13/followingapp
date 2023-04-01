from sqlalchemy.orm import Session

from db.models.users import User, ActivationToken
from services.email_service import GmailService
from core.config import settings
from db.repository.users import UserRepository

class UserActivationService:
    def __init__(self):
        self.email_service = GmailService()

    def send_email_verification_url(self, user: User):
        activation_token: ActivationToken = user.activation_token[0]
        activation_url = f"{settings.BASE_URL}/users/activate/{activation_token.token}"
        self.email_service.send_email(user.email, "Activate your account at Following App", activation_url)
    
    def activate_user_with_activation_token(self, token: str, db: Session):
        user_repository = UserRepository(db)
        user: User = user_repository.get_active_user_by_activation_token(token=token)

        if user:
            user.is_active = True
            user.activation_token[0].is_active = False
            db.commit()
        return user



    
