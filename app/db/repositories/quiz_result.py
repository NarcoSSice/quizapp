from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from db.repositories.base import BaseRepository
from models import QuizModel, UserModel
from models.quiz_results import QuizResultModel


class QuizResultRepository(BaseRepository[QuizResultModel]):
    model = QuizResultModel

    def get_loads(self) -> list:
        return [
            selectinload(self.model.user),
            selectinload(self.model.company),
            selectinload(self.model.quiz),
            selectinload(self.model.responses),
        ]

    @property
    def avg_score(self):
        return func.avg(
            (self.model.correct_answers * 1.0 / self.model.total_questions) * 100
        )

    async def get_quiz_result_with_answers(
        self, user_id: int, company_id: int, quiz_id: int
    ) -> QuizResultModel:
        query = (
            select(self.model)
            .options(*self.get_loads())
            .where(
                self.model.user_id == user_id,
                self.model.company_id == company_id,
                self.model.quiz_id == quiz_id,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_company_quiz_results(
        self, company_id: int, quiz_id: int
    ) -> list[QuizResultModel]:
        result = await self.session.execute(
            select(self.model)
            .options(*self.get_loads())
            .where(self.model.company_id == company_id, self.model.quiz_id == quiz_id)
        )
        return result.scalars().all()

    async def get_results(
        self, user_id: int, company_id: int, quiz_id: int
    ) -> QuizResultModel:
        result = await self.session.execute(
            select(self.model).where(
                self.model.user_id == user_id,
                self.model.company_id == company_id,
                self.model.quiz_id == quiz_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_user_average_result(self, user_id: int) -> float:
        result = await self.session.execute(
            select(self.avg_score).where(QuizResultModel.user_id == user_id)
        )
        average = result.scalar()
        return round(average, 2) if average else 0.0

    async def get_user_quizzes_average_scores(
        self, user_id: int
    ) -> list[tuple[QuizModel, float, datetime, datetime]]:
        result = await self.session.execute(
            select(
                QuizModel,
                self.avg_score.label("average"),
                func.min(self.model.last_attempt_at).label("first_taken"),
                func.max(self.model.last_attempt_at).label("last_taken"),
            )
            .join(QuizModel, self.model.quiz_id == QuizModel.id)
            .where(self.model.user_id == user_id)
            .group_by(QuizModel.id)
        )

        return result.all()

    async def get_user_last_completions(
        self, user_id: int
    ) -> list[tuple[QuizModel, datetime]]:
        result = await self.session.execute(
            select(
                QuizModel,
                func.max(self.model.last_attempt_at).label("last_attempt"),
            )
            .join(QuizModel, self.model.quiz_id == QuizModel.id)
            .where(self.model.user_id == user_id)
            .group_by(QuizModel.id)
        )

        return result.all()

    async def get_company_average_scores_by_week(
        self, company_id: int
    ) -> list[tuple[datetime, float]]:
        week_trunc = func.date_trunc("week", self.model.last_attempt_at)
        result = await self.session.execute(
            select(
                week_trunc.label("week"),
                self.avg_score.label("average_score"),
            )
            .where(self.model.company_id == company_id)
            .group_by(week_trunc)
        )

        return result.all()

    async def get_company_user_quiz_scores_by_week(
        self, company_id: int, user_id: int
    ) -> list[tuple[QuizModel, datetime, float]]:
        week_trunc = func.date_trunc("week", self.model.last_attempt_at)
        result = await self.session.execute(
            select(
                QuizModel,
                week_trunc.label("week"),
                self.avg_score.label("average_score"),
            )
            .join(QuizModel, QuizModel.id == self.model.quiz_id)
            .where(self.model.company_id == company_id, self.model.user_id == user_id)
            .group_by(QuizModel.id, week_trunc)
        )

        return result.all()

    async def get_company_users_last_attempt(
        self, company_id: int, quiz_id: int
    ) -> list[tuple[str, datetime]]:
        result = await self.session.execute(
            select(
                UserModel, func.max(self.model.last_attempt_at).label("last_attempt")
            )
            .join(UserModel, UserModel.id == self.model.user_id)
            .where(self.model.quiz_id == quiz_id, self.model.company_id == company_id)
            .group_by(UserModel)
        )
        return result.all()

    async def get_user_company_average_result(
        self, user_id: int, company_id: int
    ) -> float:
        result = await self.session.execute(
            select(
                (
                    func.sum(QuizResultModel.correct_answers)
                    / func.sum(QuizResultModel.total_questions)
                ).label("average")
            ).where(
                QuizResultModel.user_id == user_id,
                QuizResultModel.company_id == company_id,
            )
        )
        average = result.scalar()
        return round(float(average) * 100, 2) if average else 0.0
