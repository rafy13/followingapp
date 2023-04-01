from sqlalchemy.orm import Session
from db.models.photos import Reaction 

def fetch_reaction_by_user_id_and_photo_id(user_id: int, photo_id: int, db:Session):
    return db.query(Reaction) \
        .filter(Reaction.user_id == user_id) \
        .filter(Reaction.photo_id == photo_id) \
        .first()

def delete_reaction(reaction: Reaction, db: Session):
    db.delete(reaction)
    db.commit()

def _create_reaction(user_id: int, photo_id: int):
    reaction = Reaction(
        user_id=user_id,
        photo_id=photo_id,
    )
    return reaction

def create_like(user_id: int, photo_id: int, db:Session):
    reaction: Reaction = _create_reaction(user_id, photo_id)
    reaction.liked = True
    
    db.add(reaction)
    db.commit()

def create_dislike(user_id: int, photo_id: int, db:Session):
    reaction: Reaction = _create_reaction(user_id, photo_id)
    reaction.disliked = True
    
    db.add(reaction)
    db.commit()
