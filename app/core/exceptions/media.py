from fastapi import HTTPException


class NotSupportedExtensionsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Unsupported image format")
