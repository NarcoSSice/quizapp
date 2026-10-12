import json
from db.redis import RedisClient, redis_client
from schemas.quiz_results import ResultAnswersResponseSchema


class QuizRedisStorage:
    EXP_SECONDS: int = 172800

    def __init__(self, client: RedisClient):
        self.redis_client = client

    @staticmethod
    def _make_key(user_id: int, company_id: int, quiz_id: int) -> str:
        return f"quiz:{quiz_id}:company:{company_id}:user:{user_id}"

    async def store_quiz_results(
        self,
        user_id: int,
        company_id: int,
        quiz_id: int,
        user_answers: ResultAnswersResponseSchema,
    ):
        client = await self.redis_client.get_redis_client()
        key = self._make_key(user_id, company_id, quiz_id)

        await client.set(key, user_answers.model_dump_json(), ex=self.EXP_SECONDS)

    async def get_quiz_results(
        self,
        user_id: int,
        company_id: int,
        quiz_id: int,
    ) -> list[dict] | None:
        client = await self.redis_client.get_redis_client()
        key = self._make_key(user_id, company_id, quiz_id)
        data = await client.get(key)
        return json.loads(data) if data else None


quiz_redis = QuizRedisStorage(redis_client)
