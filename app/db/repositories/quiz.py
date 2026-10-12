from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from db.repositories.base import BaseRepository
from models import UserCompanyAssociation, CompanyModel
from models.quiz import QuizModel, QuestionModel


class QuizRepository(BaseRepository[QuizModel]):
    model = QuizModel

    async def get_quiz_by_id(self, quiz_id: int) -> QuizModel:
        quiz = await self.session.execute(
            select(self.model)
            .where(self.model.id == quiz_id)
            .options(
                selectinload(self.model.questions).selectinload(QuestionModel.answers)
            )
        )
        return quiz.scalar_one_or_none()

    async def get_by_titles(self, titles: list[str]) -> list[QuizModel]:
        result = await self.session.execute(
            select(self.model)
            .where(self.model.title.in_(titles))
            .options(
                selectinload(self.model.questions).selectinload(QuestionModel.answers)
            )
        )
        return result.scalars().all()

    async def get_company_quizzes(
        self, company_id: int, limit: int, offset: int
    ) -> tuple[list[QuizModel], int]:
        query = (
            select(self.model)
            .where(self.model.company_id == company_id)
            .options(
                selectinload(self.model.questions).selectinload(QuestionModel.answers)
            )
        )
        return await self.get_items_with_pagination(query, limit, offset)

    async def get_enable_to_user_quizzes(
        self,
        user_id: int,
    ) -> list[QuizModel]:
        results = await self.session.execute(
            select(self.model)
            .join(CompanyModel, self.model.company_id == CompanyModel.id)
            .join(
                UserCompanyAssociation,
                UserCompanyAssociation.company_id == CompanyModel.id,
            )
            .filter(UserCompanyAssociation.user_id == user_id)
        )
        return results.scalars().all()
