from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from db.uow import UnitOfWork, get_uow
from services.auth import AuthService

http_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    uow: UnitOfWork = Depends(get_uow),
    auth_service: AuthService = Depends(),
):
    return await auth_service.get_current_auth_user(uow, credentials.credentials)
