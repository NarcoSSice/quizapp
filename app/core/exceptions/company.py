from fastapi import HTTPException


class NotOwnerException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="User not owner this company")


class NotOwnerOrAdminPermissionException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403, detail="You don't have permission for this operation"
        )
