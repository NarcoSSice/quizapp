from fastapi import APIRouter, Depends, UploadFile, Request

from db.uow import UnitOfWork, get_uow
from routers.dependencies import get_current_user
from schemas.base import TokenSchema
from schemas.quiz import AverageScoreResponseSchema
from schemas.user import (
    UserSignInSchema,
    TokenUserInfoSchema,
    UserSignUpSchema,
    UserDetailSchema,
    UserUpdateSchema,
)
from services.auth import AuthService
from services.quiz import QuizService

router = APIRouter(
    tags=["auth"],
)


@router.post("/register", response_model=TokenSchema)
async def register(
    user: UserSignUpSchema,
    uow: UnitOfWork = Depends(get_uow),
    auth_service: AuthService = Depends(),
):
    token = await auth_service.register_user(uow, user)
    return TokenSchema(
        access_token=token,
        token_type="Bearer",
    )


@router.post("/login", response_model=TokenSchema)
async def login(
    credentials: UserSignInSchema,
    uow: UnitOfWork = Depends(get_uow),
    auth_service: AuthService = Depends(),
):
    token = await auth_service.login_user(uow, credentials)
    return TokenSchema(
        access_token=token,
        token_type="Bearer",
    )


@router.get("/me", response_model=UserDetailSchema)
async def current_auth_user(
    current_user: TokenUserInfoSchema = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    auth_service: AuthService = Depends(),
):
    return await auth_service.return_user_info(uow, current_user)


@router.patch("/me", response_model=UserDetailSchema)
async def update_profile(
    update_data: UserUpdateSchema,
    uow: UnitOfWork = Depends(get_uow),
    current_user: TokenUserInfoSchema = Depends(get_current_user),
    auth_service: AuthService = Depends(),
):
    return await auth_service.update_profile(uow, update_data, current_user)


@router.post("/me/upload", response_model=UserDetailSchema)
async def upload_profile_image(
    image: UploadFile,
    request: Request,
    uow: UnitOfWork = Depends(get_uow),
    current_user: TokenUserInfoSchema = Depends(get_current_user),
    auth_service: AuthService = Depends(),
):
    return await auth_service.upload_profile_image(uow, image, request, current_user)


@router.get("/me/average-score", response_model=AverageScoreResponseSchema)
async def get_my_average_score(
    user: TokenUserInfoSchema = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    quiz_service: QuizService = Depends(),
):
    return await quiz_service.get_user_average_score(uow, user)
