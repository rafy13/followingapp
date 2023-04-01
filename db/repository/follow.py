from sqlalchemy.orm import Session
from db.models.users import Follow

def fetch_follow(follower_id: int, followed_id: int, db:Session):
    return db.query(Follow) \
        .filter(Follow.follower_id == follower_id) \
        .filter(Follow.followed_id == followed_id) \
        .first()

def delete_follow(follow: Follow, db: Session):
    db.delete(follow)
    db.commit()

def create_follow(follower_id: int, followed_id: int, db:Session):
    follow = Follow(
        followed_id=followed_id,
        follower_id=follower_id,
    )
    db.add(follow)
    db.commit()
    return follow