from sqlalchemy.orm import Session
from db.models.photos import Reaction
from db.repository.base import BaseRepository


class ReactionRepository(BaseRepository[Reaction]):
    def __init__(self, db: Session):
        super().__init__(db, Reaction)
    
    def _create_reaction(self, user_id: int, photo_id: int):
        reaction = Reaction(
            user_id=user_id,
            photo_id=photo_id,
        )
        return reaction
    
    def create_like(self, user_id: int, photo_id: int):
        reaction: Reaction = self._create_reaction(user_id, photo_id)
        reaction.liked = True
        self.db.add(reaction)
        self.db.commit()
        return reaction

    def create_dislike(self, user_id: int, photo_id: int):
        reaction: Reaction = self._create_reaction(user_id, photo_id)
        reaction.disliked = True
        self.db.add(reaction)
        self.db.commit()
        return reaction

    def fetch_reaction_by_user_id_and_photo_id(self, user_id: int, photo_id: int):
        return self.db.query(Reaction) \
            .filter(Reaction.user_id == user_id) \
            .filter(Reaction.photo_id == photo_id) \
            .first()
