import uuid

from fastapi import UploadFile, Request
from jose import jwt

from core.exceptions.user import (
    UserNotFoundException,
    IncorrectPasswordException,
    EmailNotFoundInTokenException,
    InvalidTokenException,
)
from db.uow import UnitOfWork
from models.user import UserModel
from schemas.user import (
    UserSignInSchema,
    TokenUserInfoSchema,
    UserSignUpSchema,
    UserUpdateSchema,
    UserDetailSchema,
)
from services.user import UserService
from utils.media_utils import media_utils
from utils.hash import password_hasher
from utils.jwt_auth import jwt_auth


class AuthService:
    def __init__(self):
        self.user_service = UserService()

    async def register_user(self, uow: UnitOfWork, user: UserSignUpSchema):
        user = await self.user_service.create_user(uow, user)
        token = jwt_auth.generate_token(
            payload=TokenUserInfoSchema.model_validate(user.model_dump()),
        )
        return token

    async def login_user(self, uow: UnitOfWork, credentials: UserSignInSchema) -> str:
        async with uow:
            user = await uow.users.get_by_field(email=credentials.email)
            if not user:
                raise UserNotFoundException

            if not password_hasher.verify_password(
                credentials.password, user.hashed_password
            ):
                raise IncorrectPasswordException

            token = jwt_auth.generate_token(
                payload=TokenUserInfoSchema.model_validate(user),
            )
            return token

    async def _parse_auth0_token(
        self, func_uow: UnitOfWork, token: str
    ) -> TokenUserInfoSchema:
        async with func_uow:
            data = jwt_auth.validate_auth0_token(token)
            if not data["email"]:
                raise EmailNotFoundInTokenException
            user = await func_uow.users.get_by_field(email=data["email"])
            if not user:
                user = await self.user_service.create_user(
                    func_uow,
                    UserSignUpSchema(
                        email=data["email"],
                        password=uuid.uuid4().hex,
                        first_name=data["first_name"],
                        second_name=data["second_name"],
                    ),
                )
            return TokenUserInfoSchema.model_validate(
                user if isinstance(user, UserModel) else user.model_dump()
            )

    async def get_current_auth_user(
        self, uow: UnitOfWork, token: str
    ) -> TokenUserInfoSchema:
        header = jwt.get_unverified_header(token)
        if header["alg"] == "RS256":
            return await self._parse_auth0_token(uow, token)
        try:
            user = jwt_auth.decode_token(token)
        except jwt.JWTError:
            raise InvalidTokenException
        return TokenUserInfoSchema(**user)

    async def update_profile(
        self, uow: UnitOfWork, data: UserUpdateSchema, current_user: TokenUserInfoSchema
    ) -> UserDetailSchema:
        async with uow:
            user = await uow.users.get_by_field(email=current_user.email)
            updated_user = await self.user_service.update_user(uow, user.id, data)
            return updated_user

    async def upload_profile_image(
        self,
        uow: UnitOfWork,
        image: UploadFile,
        request: Request,
        current_user: TokenUserInfoSchema,
    ) -> UserDetailSchema:
        async with uow:
            image_url = await media_utils.save(image, request)
            user = await uow.users.get_by_field(email=current_user.email)
            updated_user = await self.user_service.update_user(
                uow, user.id, UserUpdateSchema(image_url=image_url)
            )
            return updated_user

    async def return_user_info(
        self, uow: UnitOfWork, user: TokenUserInfoSchema
    ) -> UserDetailSchema:
        async with uow:
            user_info = await uow.users.get_by_field(email=user.email)
            return UserDetailSchema.model_validate(user_info)
