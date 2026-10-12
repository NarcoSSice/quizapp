from fastapi import APIRouter
from schemas.index_schemas import IndexResponse

router = APIRouter()


@router.get("/", response_model=IndexResponse)
def index():
    return IndexResponse(
        status_code=200,
        detail="ok",
        result="working",
    )
