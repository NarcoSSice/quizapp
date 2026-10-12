from pydantic import BaseModel


class IndexResponse(BaseModel):
    status_code: int
    detail: str
    result: str
