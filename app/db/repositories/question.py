from sqlalchemy import select

from db.repositories.base import BaseRepository
from models.quiz import QuestionModel, AnswerModel


class QuestionRepository(BaseRepository[QuestionModel]):
    model = QuestionModel

    async def get_correct_answers(self, quiz_id: int) -> dict[int, list[int]]:
        result = await self.session.execute(
            select(self.model.id, AnswerModel.id)
            .join(AnswerModel, AnswerModel.question_id == self.model.id)
            .where(self.model.quiz_id == quiz_id, AnswerModel.is_correct == True)
        )

        correct_answers = {}
        for question_id, answer_id in result.all():
            correct_answers.setdefault(question_id, []).append(answer_id)

        return correct_answers
