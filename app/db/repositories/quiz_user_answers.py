from db.repositories.base import BaseRepository
from models import UserQuizAnswerModel


class UserQuizAnswerRepository(BaseRepository[UserQuizAnswerModel]):
    model = UserQuizAnswerModel
