from sqlalchemy.orm import Session
from db.repository.follow import fetch_follow

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def check_is_follower(self, follower_id: int, followed_id: int) -> bool:
        return fetch_follow(follower_id, followed_id, self.db) is not None

