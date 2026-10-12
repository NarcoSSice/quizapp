from fastapi import APIRouter, Depends, Query, UploadFile

from core.constants import COMPANY_ID_ROUTE, COMPANY_ROUTE
from core.enums.export import ExportType
from db.uow import UnitOfWork, get_uow
from routers.dependencies import get_current_user
from schemas.base import DeleteResponseSchema, PaginationSchema, ResponseSchema
from schemas.quiz import (
    QuizCreateSchema,
    QuizSchema,
    QuizUpdateSchema,
    UserQuizAnswerSchema,
    AverageScoreResponseSchema,
    QuizResultResponseSchema,
)
from schemas.quiz_results import (
    ResultAnswersResponseSchema,
    UserQuizAverageScoresSchema,
    UserQuizzesLastCompletionsSchema,
    CompanyUsersLastAttemptSchema,
    CompanyAverageByWeekSchema,
    CompanyUsersScoresByWeekSchema,
)
from schemas.user import TokenUserInfoSchema
from services.quiz import QuizService

router = APIRouter(
    prefix=f"{COMPANY_ROUTE}{COMPANY_ID_ROUTE}/quizzes",
    tags=["Quizzes"],
)


@router.post("/", response_model=QuizSchema)
async def create_quiz(
    company_id: int,
    quiz_data: QuizCreateSchema,
    uow: UnitOfWork = Depends(get_uow),
    user: TokenUserInfoSchema = Depends(get_current_user),
    quiz_service: QuizService = Depends(),
):
    return await quiz_service.create_quiz(uow, company_id, quiz_data, user)


@router.get("/", response_model=PaginationSchema[QuizSchema])
async def get_company_quizzes(
    company_id: int,
    limit: int = Query(10, ge=0),
    offset: int = Query(0, ge=0),
    uow: UnitOfWork = Depends(get_uow),
    quiz_service: QuizService = Depends(),
):
    return await quiz_service.get_company_quizzes(uow, company_id, limit, offset)


@router.post("/create_import", response_model=ResponseSchema)
async def create_quiz_from_import_data(
    company_id: int,
    quiz_file: UploadFile,
    uow: UnitOfWork = Depends(get_uow),
    user: TokenUserInfoSchema = Depends(get_current_user),
    quiz_service: QuizService = Depends(),
):
    return await quiz_service.create_from_import_data(uow, company_id, quiz_file, user)


@router.get("/user_averages", response_model=list[UserQuizAverageScoresSchema])
async def get_user_averages(
    user: TokenUserInfoSchema = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    quiz_service: QuizService = Depends(),
):
    return await quiz_service.get_user_quizzes_average_scores(uow, user)


@router.get(
    "/user_last_completions", response_model=list[UserQuizzesLastCompletionsSchema]
)
async def get_user_last_completions(
    user: TokenUserInfoSchema = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    quiz_service: QuizService = Depends(),
):
    return await quiz_service.get_user_quizzes_last_completion(uow, user)


@router.get("/company_average_by_week", response_model=list[CompanyAverageByWeekSchema])
async def get_company_average_by_week(
    company_id: int,
    user: TokenUserInfoSchema = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    quiz_service: QuizService = Depends(),
):
    return await quiz_service.get_company_average_by_week(uow, company_id, user)


@router.get(
    "/user_quiz_scores_by_week", response_model=list[CompanyUsersScoresByWeekSchema]
)
async def get_user_quiz_scores_by_week(
    company_id: int,
    user_id: int = Query(...),
    user: TokenUserInfoSchema = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    quiz_service: QuizService = Depends(),
):
    return await quiz_service.get_user_quiz_scores_by_week(
        uow, company_id, user_id, user
    )


@router.get(
    "/{quiz_id}/users_last_attempts", response_model=list[CompanyUsersLastAttemptSchema]
)
async def get_users_last_attempts(
    quiz_id: int,
    company_id: int,
    user: TokenUserInfoSchema = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    quiz_service: QuizService = Depends(),
):
    return await quiz_service.get_company_users_last_attenpts(
        uow, company_id, quiz_id, user
    )


@router.get("/average-score", response_model=AverageScoreResponseSchema)
async def get_my_company_average_score(
    company_id: int,
    user: TokenUserInfoSchema = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    quiz_service: QuizService = Depends(),
):
    return await quiz_service.get_user_company_average_score(uow, company_id, user)


@router.patch("/{quiz_id}", response_model=QuizSchema)
async def update_quiz(
    company_id: int,
    quiz_id: int,
    update_data: QuizUpdateSchema,
    uow: UnitOfWork = Depends(get_uow),
    user: TokenUserInfoSchema = Depends(get_current_user),
    quiz_service: QuizService = Depends(),
):
    return await quiz_service.upsert_quiz(uow, company_id, update_data, user, quiz_id)


@router.delete("/{quiz_id}", response_model=DeleteResponseSchema)
async def delete_quiz(
    company_id: int,
    quiz_id: int,
    uow: UnitOfWork = Depends(get_uow),
    user: TokenUserInfoSchema = Depends(get_current_user),
    quiz_service: QuizService = Depends(),
):
    return await quiz_service.delete_quiz(uow, company_id, quiz_id, user)


@router.get(
    "/{quiz_id}", response_model=QuizSchema, dependencies=[Depends(get_current_user)]
)
async def get_quiz(
    quiz_id: int,
    uow: UnitOfWork = Depends(get_uow),
    quiz_service: QuizService = Depends(),
):
    return await quiz_service.get_quiz(uow, quiz_id)


@router.post(
    "/{quiz_id}/submit",
    response_model=QuizResultResponseSchema,
)
async def submit_quiz(
    company_id: int,
    quiz_id: int,
    user_answers: UserQuizAnswerSchema,
    user: TokenUserInfoSchema = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    quiz_service: QuizService = Depends(),
):
    return await quiz_service.submit_quiz(uow, company_id, quiz_id, user, user_answers)


@router.get(
    "/{quiz_id}/result",
    response_model=ResultAnswersResponseSchema,
)
async def get_user_result(
    company_id: int,
    quiz_id: int,
    user_id: int | None = Query(None),
    user: TokenUserInfoSchema = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    quiz_service: QuizService = Depends(),
):
    return await quiz_service.get_user_result(uow, company_id, quiz_id, user, user_id)


@router.get("/{quiz_id}/results", response_model=list[ResultAnswersResponseSchema])
async def get_company_quiz_results(
    company_id: int,
    quiz_id: int,
    user: TokenUserInfoSchema = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    quiz_service: QuizService = Depends(),
):
    return await quiz_service.get_company_quiz_results(uow, company_id, quiz_id, user)


@router.get("/{quiz_id}/export_results")
async def export_company_quiz_results(
    company_id: int,
    quiz_id: int,
    export_type: ExportType = Query(ExportType.csv),
    user: TokenUserInfoSchema = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    quiz_service: QuizService = Depends(),
):
    return await quiz_service.export_company_quiz_results(
        uow, company_id, quiz_id, user, export_type
    )
