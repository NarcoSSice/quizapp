from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from db.database import async_session_maker
from db.repositories.action import ActionRepository
from db.repositories.answer import AnswerRepository
from db.repositories.company import CompanyRepository
from db.repositories.notification import NotificationRepository
from db.repositories.question import QuestionRepository
from db.repositories.quiz import QuizRepository
from db.repositories.quiz_result import QuizResultRepository
from db.repositories.quiz_user_answers import UserQuizAnswerRepository
from db.repositories.user import UserRepository
from db.repositories.user_company_association import UserCompanyAssociationRepository


class UnitOfWork:
    def __init__(
        self, session_maker: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        self.session_maker = session_maker

    async def __aenter__(self):
        self.session = self.session_maker()
        self.users = UserRepository(self.session)
        self.actions = ActionRepository(self.session)
        self.companies = CompanyRepository(self.session)
        self.user_company_association = UserCompanyAssociationRepository(self.session)
        self.quizzes = QuizRepository(self.session)
        self.questions = QuestionRepository(self.session)
        self.answers = AnswerRepository(self.session)
        self.quiz_results = QuizResultRepository(self.session)
        self.quiz_user_answers = UserQuizAnswerRepository(self.session)
        self.notifications = NotificationRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def refresh(self, obj):
        await self.session.refresh(obj)

    async def close(self):
        await self.session.close()


async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    async with UnitOfWork() as uow:
        yield uow
