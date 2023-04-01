from sqlalchemy.orm import Session
from db.models.users import Follow
from db.repository.base import BaseRepository

class FollowRepository(BaseRepository[Follow]):
    def __init__(self, db: Session):
        super().__init__(db, Follow)
    
    def get_by_follower_id_followed_id(self, follower_id: int, followed_id: int):
        return self.db.query(Follow) \
            .filter(Follow.follower_id == follower_id) \
            .filter(Follow.followed_id == followed_id) \
            .first()
    
    def create(self, **kwargs):
        follow = Follow(**kwargs)
        super().create(follow)
        return follow