from db.repositories.base import BaseRepository
from models import AnswerModel


class AnswerRepository(BaseRepository[AnswerModel]):
    model = AnswerModel
