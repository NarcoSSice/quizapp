import random
from datetime import datetime

import factory
from faker import Faker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from core.enums.action import ActionType, ActionStatus
from core.enums.company_association import RoleType
from core.enums.notification import NotificationStatus
from models import *
from utils.hash import password_hasher

TEST_URL = "postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db"
test_engine = create_async_engine(TEST_URL)
test_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)

faker = Faker()


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session_factory = test_session_maker

    @classmethod
    async def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        async with cls._meta.sqlalchemy_session as session:
            await session.commit()
        return instance


class UserFactory(BaseFactory):
    class Meta:
        model = UserModel

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    hashed_password = factory.LazyAttribute(lambda _: password_hasher.hash("string"))
    first_name = factory.LazyAttribute(lambda _: faker.first_name())
    second_name = factory.LazyAttribute(lambda _: faker.last_name())


class CompanyFactory(BaseFactory):
    class Meta:
        model = CompanyModel

    name = factory.LazyAttribute(lambda _: faker.company())
    description = factory.LazyAttribute(lambda _: faker.text(max_nb_chars=200))
    is_hidden = factory.Faker("boolean")
    owner_id = factory.SubFactory(UserFactory)


class ActionFactory(BaseFactory):
    class Meta:
        model = CompanyActionsModel

    company_id = factory.SubFactory(CompanyFactory)
    user_id = factory.SubFactory(UserFactory)
    action_type = factory.Iterator(list(ActionType))
    status = factory.LazyFunction(lambda: ActionStatus.pending)


class UserCompanyAssociationFactory(BaseFactory):
    class Meta:
        model = UserCompanyAssociation

    user_id = factory.SubFactory(UserFactory)
    company_id = factory.SubFactory(CompanyFactory)
    role = factory.LazyFunction(lambda: RoleType.member)


class QuizFactory(BaseFactory):
    class Meta:
        model = QuizModel

    title = factory.Faker("sentence")
    description = factory.Faker("text")
    company_id = factory.SubFactory(CompanyFactory)


class QuestionFactory(BaseFactory):
    class Meta:
        model = QuestionModel

    title = factory.Faker("sentence")
    quiz_id = factory.SubFactory(QuizFactory)


class AnswerFactory(BaseFactory):
    class Meta:
        model = AnswerModel

    text = factory.Faker("word")
    is_correct = False
    question_id = factory.SubFactory(QuestionFactory)


class QuizResultFactory(BaseFactory):
    class Meta:
        model = QuizResultModel

    user_id = factory.SubFactory(UserFactory)
    company_id = factory.SubFactory(CompanyFactory)
    quiz_id = factory.SubFactory(QuizFactory)

    total_questions = 5
    answered_questions = factory.LazyAttribute(
        lambda o: random.randint(0, o.total_questions)
    )
    correct_answers = factory.LazyAttribute(
        lambda o: random.randint(0, o.answered_questions)
    )
    last_attempt_at = factory.LazyFunction(datetime.now)


class UserQuizAnswerFactory(BaseFactory):
    class Meta:
        model = UserQuizAnswerModel

    quiz_result_id = factory.SubFactory(QuizResultFactory)
    question_id = factory.SubFactory(QuestionFactory)

    user_answer = factory.LazyFunction(lambda: [random.randint(1, 2)])
    is_correct = factory.LazyFunction(lambda: random.choice([True, False]))


class NotificationFactory(BaseFactory):
    class Meta:
        model = NotificationModel

    user_id = factory.SubFactory(UserFactory)
    message = factory.Faker("text")
    status = NotificationStatus.unread
