from datetime import datetime, timedelta
from db.uow import UnitOfWork


async def check_user_quizzes():
    async with UnitOfWork() as uow:
        now = datetime.now()
        users = await uow.users.get_all()

        notifications = []
        for user in users:
            available_quizzes = await uow.quizzes.get_enable_to_user_quizzes(user.id)
            user_completions = await uow.quiz_results.get_user_last_completions(user.id)

            completions_dict = {
                quiz.id: last_attempt for quiz, last_attempt in user_completions
            }

            for quiz in available_quizzes:
                last_attempt = completions_dict.get(quiz.id)

                if not last_attempt or (now - last_attempt) > timedelta(hours=24):
                    notifications.append(
                        dict(
                            message=f"Don't forget take a quiz: {quiz.title}",
                            user_id=user.id,
                        )
                    )

        await uow.notifications.create_many(notifications)
