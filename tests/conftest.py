import asyncio

import pytest_asyncio

from core.enums.company_association import RoleType
from db.uow import UnitOfWork
from models.base import Base
from services.action import ActionService
from services.auth import AuthService
from services.company import CompanyService
from services.notification import NotificationService
from services.quiz import QuizService
from services.user import UserService
from tests.db.db import (
    test_engine,
    test_session_maker,
    UserFactory,
    CompanyFactory,
    UserCompanyAssociationFactory,
    QuestionFactory,
    QuizFactory,
    AnswerFactory,
    QuizResultFactory,
    UserQuizAnswerFactory,
)

user_data = UserFactory.build(email="example@gmail.com")
company_data = CompanyFactory.build(name="Example Company")


async def create_user():
    user = await UserFactory.create(email="example@gmail.com")
    return user.id


async def create_company(user_id):
    company = await CompanyFactory.create(name="Example Company", owner_id=user_id)
    await UserCompanyAssociationFactory.create(
        user_id=user_id, company_id=company.id, role=RoleType.owner
    )
    return company.id


@pytest_asyncio.fixture
async def quiz():
    user = await UserFactory.create()
    company_id = await create_company(user.id)
    quiz = await QuizFactory.create(company_id=company_id)

    q1 = await QuestionFactory.create(quiz_id=quiz.id)
    q2 = await QuestionFactory.create(quiz_id=quiz.id)

    a1_q1 = await AnswerFactory.create(question_id=q1.id, is_correct=True)
    a2_q1 = await AnswerFactory.create(question_id=q1.id, is_correct=False)
    a1_q2 = await AnswerFactory.create(question_id=q2.id, is_correct=True)
    a2_q2 = await AnswerFactory.create(question_id=q2.id, is_correct=False)

    return {
        "user": user,
        "company_id": company_id,
        "quiz": quiz,
        "questions": [q1, q2],
        "answers": {
            q1.id: [a1_q1, a2_q1],
            q2.id: [a1_q2, a2_q2],
        },
    }


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def quiz_result(quiz):
    quiz_result = await QuizResultFactory.create(
        user_id=quiz["user"].id,
        company_id=quiz["company_id"],
        quiz_id=quiz["quiz"].id,
        total_questions=len(quiz["questions"]),
        answered_questions=2,
        correct_answers=1,
    )
    result_answer1 = await UserQuizAnswerFactory.create(
        quiz_result_id=quiz_result.id,
        question_id=quiz["questions"][0].id,
        user_answer=[quiz["answers"][quiz["questions"][0].id][0].id],
    )
    result_answer2 = await UserQuizAnswerFactory.create(
        quiz_result_id=quiz_result.id,
        question_id=quiz["questions"][1].id,
        user_answer=[quiz["answers"][quiz["questions"][1].id][1].id],
    )
    return {
        "quiz_result": quiz_result,
        "result_answer1": result_answer1,
        "result_answer2": result_answer2,
    }


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    user_id = await create_user()
    await create_company(user_id)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    session = test_session_maker()
    try:
        yield session
    finally:
        await session.close()


@pytest_asyncio.fixture(scope="function")
async def uow():
    async with UnitOfWork(test_session_maker) as uow:
        yield uow


services = {
    "user_service": UserService,
    "company_service": CompanyService,
    "auth_service": AuthService,
    "action_service": ActionService,
    "quiz_service": QuizService,
    "notification_service": NotificationService,
}

for name, cls in services.items():

    @pytest_asyncio.fixture(scope="function", name=name)
    async def service_fixture(clss=cls):
        yield clss()

    globals()[name] = service_fixture
