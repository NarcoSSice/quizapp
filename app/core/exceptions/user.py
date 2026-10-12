from fastapi import HTTPException


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User not found")


class UserExistEmailException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User with this email already exist")


class IncorrectPasswordException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Incorrect password")


class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid token error")


class EmailNotFoundInTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Email not found in token")


class NoDeleteUserPermission(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="You can't delete this user")
