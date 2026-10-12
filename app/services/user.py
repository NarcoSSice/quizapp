from core.exceptions.user import (
    UserNotFoundException,
    UserExistEmailException,
    NoDeleteUserPermission,
)
from core.logger import logger
from db.uow import UnitOfWork
from schemas.base import PaginationSchema, DeleteResponseSchema
from schemas.company import UserWithCompaniesSchema
from schemas.user import (
    UserSignUpSchema,
    UserDetailSchema,
    UserUpdateSchema,
    UserCompanySchema,
    TokenUserInfoSchema,
)
from utils.hash import password_hasher


class UserService:
    def _update_password(self, data: dict) -> dict:
        hash_pass = password_hasher.hash(data["password"])
        data.pop("password")
        data["hashed_password"] = hash_pass
        return data

    async def get_all_users(
        self, uow: UnitOfWork, limit: int, offset: int
    ) -> PaginationSchema:
        async with uow:
            items, count = await uow.users.get_all_users(limit, offset)
            return PaginationSchema[UserWithCompaniesSchema](
                count=count,
                items=[UserWithCompaniesSchema.model_validate(user) for user in items],
            )

    async def get_user_by_id(
        self, uow: UnitOfWork, user_id: int
    ) -> UserWithCompaniesSchema:
        async with uow:
            user = await uow.users.get_user_by_id(user_id)
            if user is None:
                logger.warning(f"Attempt to get user with a non-existent id")
                raise UserNotFoundException
            return user

    async def create_user(
        self, uow: UnitOfWork, data: UserSignUpSchema
    ) -> UserDetailSchema:
        async with uow:
            exist_user = await uow.users.get_by_field(email=data.email)
            if exist_user:
                logger.warning(
                    f"Attempt to create user with existing email: {data.email}"
                )
                raise UserExistEmailException
            data = self._update_password(data.model_dump())
            new_user = await uow.users.create(data)
            await uow.session.flush()
            logger.info(f"Create new user: {new_user.id}")
            return UserDetailSchema.model_validate(new_user)

    async def update_user(
        self, uow: UnitOfWork, user_id: int, data: UserUpdateSchema
    ) -> UserDetailSchema:
        data = data.model_dump(exclude_none=True)
        if "password" in data:
            data = self._update_password(data)
        async with uow:
            await uow.users.update(user_id, data)
            upd_user = await uow.users.get_by_field(id=user_id)
            logger.info(f"Update user: {user_id}")
            return UserDetailSchema.model_validate(upd_user)

    async def delete_user(
        self, uow: UnitOfWork, user_id: int, current_user: TokenUserInfoSchema
    ) -> DeleteResponseSchema:
        async with uow:
            user = await uow.users.get_by_field(email=current_user.email)
            if not user.id == user_id:
                raise NoDeleteUserPermission
            await uow.users.delete(user_id)
        logger.info(f"Delete user {user_id}")
        return DeleteResponseSchema(status="user deleted")

    async def get_all_user_companies(
        self, uow: UnitOfWork, user_id: int
    ) -> list[UserCompanySchema]:
        async with uow:
            associations = await uow.user_company_association.get_all_user_companies(
                user_id
            )
            return [
                UserCompanySchema(
                    company_id=data.company.id,
                    company_name=data.company.name,
                    role=data.role,
                )
                for data in associations
            ]
