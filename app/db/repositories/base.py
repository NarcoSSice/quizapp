from typing import Tuple

from sqlalchemy import select, update, delete, func, Select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository[ModelType]:
    model: type[ModelType]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, **kwargs) -> list[ModelType]:
        result = await self.session.execute(select(self.model).filter_by(**kwargs))
        return result.scalars().all()

    async def get_by_field(self, **kwargs) -> ModelType | None:
        query = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> ModelType:
        new_obj = self.model(**data)
        self.session.add(new_obj)
        return new_obj

    async def update(self, obj_id: int, data: dict) -> None:
        await self.session.execute(
            update(self.model).where(self.model.id == obj_id).values(**data)
        )

    async def delete(self, obj_id: int) -> None:
        await self.session.execute(delete(self.model).where(self.model.id == obj_id))

    async def create_many(self, data: list[dict]) -> list[ModelType]:
        objcts = [self.model(**obj_data) for obj_data in data]
        self.session.add_all(objcts)
        return objcts

    async def get_items_with_pagination(
        self, query: Select, limit: int, offset: int
    ) -> Tuple[list[ModelType], int]:
        query = (
            query.add_columns(func.count().over().label("total_count"))
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        rows = result.all()

        items = [row[0] for row in rows]
        count = rows[0][1] if rows else 0

        return items, count
