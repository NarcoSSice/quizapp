import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from core.enums.export import ExportType
from db.uow import UnitOfWork
from models import QuizModel
from schemas.answer import AnswerCreateSchema, AnswerUpdateSchema
from schemas.question import QuestionCreateSchema, QuestionUpdateSchema
from schemas.quiz import QuizCreateSchema, QuizUpdateSchema
from schemas.user import TokenUserInfoSchema
from services.quiz import QuizService
from tests.db.db import QuizFactory
from tests.test_company import user_token_data


@pytest.mark.asyncio
async def test_create_quiz(
    uow: UnitOfWork, quiz_service: QuizService, db_session: AsyncSession
):
    quiz_data = QuizCreateSchema(
        title="New Quiz",
        description="Description",
        questions=[
            QuestionCreateSchema(
                title="Q1",
                answers=[
                    AnswerCreateSchema(text="A1", is_correct=True),
                    AnswerCreateSchema(text="A2", is_correct=False),
                ],
            ),
            QuestionCreateSchema(
                title="Q1",
                answers=[
                    AnswerCreateSchema(text="B1", is_correct=False),
                    AnswerCreateSchema(text="B2", is_correct=True),
                ],
            ),
        ],
    )

    result = await quiz_service.create_quiz(uow, 1, quiz_data, user_token_data)

    assert result.title == "New Quiz"
    assert len(result.questions) == 2
    assert result.questions[0].answers[0].text == "A1"

    result = await db_session.execute(
        select(QuizModel).where(QuizModel.id == result.id)
    )
    quiz = result.scalar_one_or_none()
    assert quiz is not None


@pytest.mark.asyncio
async def test_create_quiz_validation_error():
    with pytest.raises(ValidationError):
        QuizCreateSchema(
            title="Invalid Quiz",
            description="Description",
            questions=[
                QuestionCreateSchema(
                    title="Q1",
                    answers=[
                        AnswerCreateSchema(text="A1", is_correct=True),
                    ],
                )
            ],
        )


@pytest.mark.asyncio
async def test_update_quiz(uow: UnitOfWork, quiz: dict, quiz_service: QuizService):
    user = TokenUserInfoSchema.model_validate(quiz["user"])
    q1 = quiz["questions"][0]
    answers_q1 = quiz["answers"][q1.id]

    update_data = QuizUpdateSchema(
        title="Updated quiz title",
        questions=[
            QuestionUpdateSchema(
                id=q1.id,
                title="Updated question title",
                answers=[
                    AnswerUpdateSchema(
                        id=answers_q1[0].id,
                        text="Updated answer 1",
                        is_correct=True,
                    ),
                    AnswerUpdateSchema(
                        id=answers_q1[1].id,
                        text="Updated answer 2",
                        is_correct=False,
                    ),
                ],
            ),
            QuestionUpdateSchema(
                title="New question title",
                answers=[
                    AnswerUpdateSchema(
                        text="New answer 1",
                        is_correct=True,
                    ),
                    AnswerUpdateSchema(
                        text="New answer 2",
                        is_correct=False,
                    ),
                ],
            ),
        ],
    )

    updated_quiz = await quiz_service.upsert_quiz(
        uow, quiz["company_id"], update_data, user, quiz["quiz"].id
    )

    assert updated_quiz.title == "Updated quiz title"
    assert len(updated_quiz.questions) == 3


@pytest.mark.asyncio
async def test_delete_quiz(
    uow: UnitOfWork, quiz: dict, quiz_service: QuizService, db_session: AsyncSession
):
    user = TokenUserInfoSchema.model_validate(quiz["user"])
    response = await quiz_service.delete_quiz(
        uow, quiz["company_id"], quiz["quiz"].id, user
    )

    assert response.status == "Quiz deleted successfully"

    result = await db_session.execute(
        select(QuizModel).where(QuizModel.id == quiz["quiz"].id)
    )
    deleted_quiz = result.scalar_one_or_none()
    assert deleted_quiz is None


@pytest.mark.asyncio
async def test_get_company_quizzes(
    uow: UnitOfWork, quiz: dict, quiz_service: QuizService
):
    for _ in range(5):
        await QuizFactory.create(company_id=quiz["company_id"])

    result_page1 = await quiz_service.get_company_quizzes(
        uow, quiz["company_id"], limit=2, offset=0
    )
    result_page2 = await quiz_service.get_company_quizzes(
        uow, quiz["company_id"], limit=2, offset=2
    )

    assert result_page1.count == result_page2.count
    assert result_page1.items[0].id != result_page2.items[0].id
    assert len(result_page1.items) == 2
    assert len(result_page2.items) == 2


@pytest.mark.asyncio
async def test_get_quiz(uow: UnitOfWork, quiz: dict, quiz_service: QuizService):
    result = await quiz_service.get_quiz(uow, quiz["quiz"].id)
    assert result is not None
    assert result.id == quiz["quiz"].id


@pytest.mark.asyncio
async def test_get_user_average_score(
    uow: UnitOfWork, quiz: dict, quiz_service: QuizService, quiz_result: dict
):
    user = TokenUserInfoSchema.model_validate(quiz["user"])

    result = await quiz_service.get_user_average_score(uow, user)

    assert result is not None
    assert result.score == 50.0


@pytest.mark.asyncio
async def test_get_user_quizzes_average_scores(
    uow: UnitOfWork, quiz: dict, quiz_service: QuizService, quiz_result: dict
):
    user = TokenUserInfoSchema.model_validate(quiz["user"])
    result = await quiz_service.get_user_quizzes_average_scores(uow, user)

    assert len(result) >= 1
    assert result[0].score == 50.0
    assert result[0].last_taken == quiz_result["quiz_result"].last_attempt_at


@pytest.mark.asyncio
async def test_get_user_quizzes_last_completion(
    uow: UnitOfWork, quiz: dict, quiz_service: QuizService, quiz_result: dict
):
    user = TokenUserInfoSchema.model_validate(quiz["user"])

    result = await quiz_service.get_user_quizzes_last_completion(uow, user)

    assert len(result) >= 1
    assert result[0].quiz_id == quiz["quiz"].id
    assert result[0].last_attempt == quiz_result["quiz_result"].last_attempt_at


@pytest.mark.asyncio
async def test_get_company_average_by_week(
    uow: UnitOfWork, quiz: dict, quiz_service: QuizService, quiz_result: dict
):
    user = TokenUserInfoSchema.model_validate(quiz["user"])

    result = await quiz_service.get_company_average_by_week(
        uow, quiz["company_id"], user
    )

    assert result[0].score == 50.0


@pytest.mark.asyncio
async def test_get_user_company_average_score(
    uow: UnitOfWork, quiz: dict, quiz_service: QuizService, quiz_result: dict
):
    user = TokenUserInfoSchema.model_validate(quiz["user"])
    result = await quiz_service.get_user_company_average_score(
        uow, quiz["company_id"], user
    )

    assert result.score == 50.0


@pytest.mark.asyncio
async def test_get_company_quiz_results(
    uow: UnitOfWork, quiz: dict, quiz_service: QuizService, quiz_result: dict
):
    user = TokenUserInfoSchema.model_validate(quiz["user"])

    result = await quiz_service.get_company_quiz_results(
        uow, quiz["company_id"], quiz["quiz"].id, user
    )

    assert result is not None
    assert result[0].user_email == user.email
    assert result[0].total_questions == quiz_result["quiz_result"].total_questions
    assert result[0].answered_questions == quiz_result["quiz_result"].answered_questions


@pytest.mark.asyncio
async def test_export_company_quiz_results(
    uow: UnitOfWork, quiz: dict, quiz_service: QuizService, quiz_result: dict
):
    user = TokenUserInfoSchema.model_validate(quiz["user"])
    result = await quiz_service.export_company_quiz_results(
        uow, quiz["company_id"], quiz["quiz"].id, user, ExportType.csv
    )

    assert isinstance(result, StreamingResponse)
    assert result.media_type == "text/csv"
    assert (
        "attachment; filename=quiz_1_results.csv"
        in result.headers["Content-Disposition"]
    )
