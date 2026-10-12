from fastapi import UploadFile

from core.enums.export import ExportType
from core.exceptions.company import NotOwnerOrAdminPermissionException
from core.logger import logger
from db.repositories.redis.redis_store import quiz_redis
from db.uow import UnitOfWork
from models import QuizResultModel, QuizModel
from schemas.answer import AnswerUpdateSchema
from schemas.base import DeleteResponseSchema, PaginationSchema, ResponseSchema
from schemas.question import QuestionUpdateSchema, QuestionCreateSchema
from schemas.quiz import (
    QuizCreateSchema,
    QuizSchema,
    QuizUpdateSchema,
    UserQuizAnswerSchema,
    QuizResultResponseSchema,
    AverageScoreResponseSchema,
)
from schemas.quiz_results import (
    CompanyExportQuizResultsSchema,
    ResultAnswersResponseSchema,
    UserResponsesSchema,
    UserQuizAverageScoresSchema,
    UserQuizzesLastCompletionsSchema,
    CompanyAverageByWeekSchema,
    CompanyUsersScoresByWeekSchema,
    CompanyUsersLastAttemptSchema,
)
from schemas.user import TokenUserInfoSchema
from utils.export_utils import data_manager


class QuizService:
    async def _admin_or_owner(
        self, func_uow: UnitOfWork, user: TokenUserInfoSchema, company_id: int
    ) -> bool:
        async with func_uow:
            user = await func_uow.users.get_by_field(email=user.email)
            association = await func_uow.user_company_association.get_by_field(
                user_id=user.id, company_id=company_id
            )
            return association.role in ("admin", "owner")

    @staticmethod
    async def _send_notifications(
        func_uow: UnitOfWork, company_id: int, quiz: QuizModel
    ) -> None:
        company_users = await func_uow.user_company_association.get_all(
            company_id=company_id
        )

        notifications = [
            dict(
                message=f"Take a new quiz in your company: {quiz.title}",
                user_id=user_assoc.user_id,
            )
            for user_assoc in company_users
        ]

        await func_uow.notifications.create_many(notifications)

    def _evaluate_quiz(
        self, user_answers: UserQuizAnswerSchema, correct_answers: dict[int, list[int]]
    ):
        total_questions = len(correct_answers)
        correct_count = 0
        answered_count = 0

        user_responses = []

        for answer in user_answers.answers:
            selected = set(answer.selected_answers)
            correct = set(correct_answers.get(answer.question_id, []))

            if not selected:
                continue

            answered_count += 1

            if selected == correct:
                correct_count += 1

            user_responses.append(
                {
                    "question_id": answer.question_id,
                    "user_answer": answer.selected_answers,
                    "is_correct": selected == correct,
                }
            )

        return total_questions, correct_count, answered_count, user_responses

    @staticmethod
    def _map_result(result: QuizResultModel):
        return ResultAnswersResponseSchema(
            user_email=result.user.email,
            company_name=result.company.name,
            quiz_title=result.quiz.title,
            total_questions=result.total_questions,
            answered_questions=result.answered_questions,
            correct_answers=result.correct_answers,
            responses=[
                UserResponsesSchema.model_validate(resp) for resp in result.responses
            ],
        )

    async def upsert_question(
        self,
        func_uow: UnitOfWork,
        questions_data: list[QuestionUpdateSchema],
        quiz_id: int,
    ) -> dict[int, list[AnswerUpdateSchema]]:
        to_update = []
        to_create = []
        answers_map = dict()

        for q in questions_data:
            data = q.model_dump(exclude_none=True, exclude={"answers", "id"})
            if q.id:
                if data:
                    to_update.append((q.id, data))
                if q.answers:
                    answers_map[q.id] = q.answers
            else:
                to_create.append(q)

        for q_id, data in to_update:
            await func_uow.questions.update(q_id, data)

        questions_data = [
            dict(quiz_id=quiz_id, title=question.title) for question in to_create
        ]
        new_questions = await func_uow.questions.create_many(questions_data)
        await func_uow.session.flush()

        for new_question, original_question in zip(new_questions, to_create):
            answers_map[new_question.id] = original_question.answers

        return answers_map

    async def upsert_answer(
        self, func_uow: UnitOfWork, answers_data: dict[int, list[AnswerUpdateSchema]]
    ) -> None:
        to_update = []
        to_create = []

        for question_id, answers in answers_data.items():
            for ans in answers:
                data = ans.model_dump(exclude_none=True, exclude={"id"})
                if ans.id:
                    if data:
                        to_update.append((ans.id, data))
                else:
                    data["question_id"] = question_id
                    to_create.append(data)

        for a_id, data in to_update:
            await func_uow.answers.update(a_id, data)

        if to_create:
            await func_uow.answers.create_many(to_create)

    async def create_quiz(
        self,
        uow: UnitOfWork,
        company_id: int,
        quiz_data: QuizCreateSchema,
        user: TokenUserInfoSchema,
    ) -> QuizSchema:
        async with uow:
            if not await self._admin_or_owner(uow, user, company_id):
                raise NotOwnerOrAdminPermissionException

            quiz = await uow.quizzes.create(
                dict(
                    company_id=company_id,
                    title=quiz_data.title,
                    description=quiz_data.description,
                )
            )
            await uow.session.flush()

            await self._send_notifications(uow, company_id, quiz)

            questions_data = [
                dict(quiz_id=quiz.id, title=question.title)
                for question in quiz_data.questions
            ]
            new_questions = await uow.questions.create_many(questions_data)
            await uow.session.flush()

            answers = []
            for new_question, original_question in zip(
                new_questions, quiz_data.questions
            ):
                answers.extend(
                    [
                        dict(
                            question_id=new_question.id,
                            text=answer.text,
                            is_correct=answer.is_correct,
                        )
                        for answer in original_question.answers
                    ]
                )
            await uow.answers.create_many(answers)

            return QuizSchema.model_validate(await uow.quizzes.get_quiz_by_id(quiz.id))

    async def upsert_quiz(
        self,
        uow: UnitOfWork,
        company_id: int,
        update_data: QuizUpdateSchema,
        user: TokenUserInfoSchema,
        quiz_id: int,
    ) -> QuizSchema:
        async with uow:
            if not await self._admin_or_owner(uow, user, company_id):
                raise NotOwnerOrAdminPermissionException

            if quiz_data := update_data.model_dump(
                exclude_none=True, exclude={"questions"}
            ):
                await uow.quizzes.update(quiz_id, quiz_data)

            if update_data.questions:
                answers_list = await self.upsert_question(
                    uow, update_data.questions, quiz_id
                )
                if answers_list:
                    await self.upsert_answer(uow, answers_list)
            await uow.session.flush()
            return QuizSchema.model_validate(await uow.quizzes.get_quiz_by_id(quiz_id))

    async def delete_quiz(
        self, uow: UnitOfWork, company_id: int, quiz_id: int, user: TokenUserInfoSchema
    ) -> DeleteResponseSchema:
        async with uow:
            if not await self._admin_or_owner(uow, user, company_id):
                raise NotOwnerOrAdminPermissionException

            await uow.quizzes.delete(quiz_id)
            return DeleteResponseSchema(status="Quiz deleted successfully")

    async def get_company_quizzes(
        self, uow: UnitOfWork, company_id: int, limit: int, offset: int
    ) -> PaginationSchema[QuizSchema]:
        async with uow:
            items, count = await uow.quizzes.get_company_quizzes(
                company_id, limit, offset
            )
            return PaginationSchema[QuizSchema](
                count=count,
                items=[QuizSchema.model_validate(quiz) for quiz in items],
            )

    async def get_quiz(self, uow: UnitOfWork, quiz_id: int) -> QuizSchema:
        async with uow:
            return await uow.quizzes.get_quiz_by_id(quiz_id)

    async def submit_quiz(
        self,
        uow: UnitOfWork,
        company_id: int,
        quiz_id: int,
        user_info: TokenUserInfoSchema,
        user_answers: UserQuizAnswerSchema,
    ) -> QuizResultResponseSchema:
        correct_answers = await uow.questions.get_correct_answers(quiz_id)
        total_questions, correct_count, answered_count, user_responses = (
            self._evaluate_quiz(user_answers, correct_answers)
        )

        user = await uow.users.get_by_field(email=user_info.email)
        result = await uow.quiz_results.create(
            dict(
                user_id=user.id,
                company_id=company_id,
                quiz_id=quiz_id,
                total_questions=total_questions,
                answered_questions=answered_count,
                correct_answers=correct_count,
            )
        )
        await uow.session.flush()

        user_responses = [
            {**resp, "quiz_result_id": result.id} for resp in user_responses
        ]
        await uow.quiz_user_answers.create_many(user_responses)

        score = round(correct_count / total_questions * 100, 2)
        return QuizResultResponseSchema(score=score, correct_answers=correct_count)

    @staticmethod
    async def get_user_average_score(
        uow: UnitOfWork, user_info: TokenUserInfoSchema
    ) -> AverageScoreResponseSchema:
        user = await uow.users.get_by_field(email=user_info.email)

        score = await uow.quiz_results.get_user_average_result(user.id)
        return AverageScoreResponseSchema(score=score)

    @staticmethod
    async def get_user_quizzes_average_scores(
        uow: UnitOfWork, user_info: TokenUserInfoSchema
    ) -> list[UserQuizAverageScoresSchema]:
        user = await uow.users.get_by_field(email=user_info.email)

        results = await uow.quiz_results.get_user_quizzes_average_scores(user.id)
        return [
            UserQuizAverageScoresSchema(
                quiz_id=quiz.id,
                quiz_title=quiz.title,
                score=round(avg, 2),
                first_taken=first_taken,
                last_taken=last_taken,
            )
            for quiz, avg, first_taken, last_taken in results
        ]

    @staticmethod
    async def get_user_quizzes_last_completion(
        uow: UnitOfWork, user_info: TokenUserInfoSchema
    ) -> list[UserQuizzesLastCompletionsSchema]:
        user = await uow.users.get_by_field(email=user_info.email)

        results = await uow.quiz_results.get_user_last_completions(user.id)
        return [
            UserQuizzesLastCompletionsSchema(
                quiz_id=quiz.id, quiz_title=quiz.title, last_attempt=last_attempt
            )
            for quiz, last_attempt in results
        ]

    async def get_company_average_by_week(
        self, uow: UnitOfWork, company_id: int, user_info: TokenUserInfoSchema
    ) -> list[CompanyAverageByWeekSchema]:
        if not await self._admin_or_owner(uow, user_info, company_id):
            raise NotOwnerOrAdminPermissionException

        results = await uow.quiz_results.get_company_average_scores_by_week(company_id)
        return [
            CompanyAverageByWeekSchema(week=week, score=round(avg, 2))
            for week, avg in results
        ]

    async def get_user_quiz_scores_by_week(
        self,
        uow: UnitOfWork,
        company_id: int,
        user_id: int,
        user_info: TokenUserInfoSchema,
    ) -> list[CompanyUsersScoresByWeekSchema]:
        if not await self._admin_or_owner(uow, user_info, company_id):
            raise NotOwnerOrAdminPermissionException

        results = await uow.quiz_results.get_company_user_quiz_scores_by_week(
            company_id, user_id
        )
        return [
            CompanyUsersScoresByWeekSchema(
                quiz_id=quiz.id, quiz_title=quiz.title, week=week, score=round(avg, 2)
            )
            for quiz, week, avg in results
        ]

    async def get_company_users_last_attenpts(
        self,
        uow: UnitOfWork,
        company_id: int,
        quiz_id: int,
        user_info: TokenUserInfoSchema,
    ) -> list[CompanyUsersLastAttemptSchema]:
        if not await self._admin_or_owner(uow, user_info, company_id):
            raise NotOwnerOrAdminPermissionException

        results = await uow.quiz_results.get_company_users_last_attempt(
            company_id, quiz_id
        )
        return [
            CompanyUsersLastAttemptSchema(
                user_email=user.email, last_attempt=last_attempt
            )
            for user, last_attempt in results
        ]

    @staticmethod
    async def get_user_company_average_score(
        uow: UnitOfWork, company_id, user_info: TokenUserInfoSchema
    ) -> AverageScoreResponseSchema:
        user = await uow.users.get_by_field(email=user_info.email)

        score = await uow.quiz_results.get_user_company_average_result(
            user.id, company_id
        )
        return AverageScoreResponseSchema(score=score)

    async def get_user_result(
        self,
        uow: UnitOfWork,
        company_id: int,
        quiz_id: int,
        user_info: TokenUserInfoSchema,
        user_id: int | None = None,
    ) -> ResultAnswersResponseSchema:
        if user_id:
            if not await self._admin_or_owner(uow, user_info, company_id):
                raise NotOwnerOrAdminPermissionException
        else:
            user = await uow.users.get_by_field(email=user_info.email)
            user_id = user.id

        cache_results = await quiz_redis.get_quiz_results(user_id, company_id, quiz_id)
        if cache_results:
            return cache_results

        result = await uow.quiz_results.get_quiz_result_with_answers(
            user_id, company_id, quiz_id
        )
        data = self._map_result(result)

        await quiz_redis.store_quiz_results(user_id, company_id, quiz_id, data)

        return data

    async def get_company_quiz_results(
        self,
        uow: UnitOfWork,
        company_id: int,
        quiz_id: int,
        user_info: TokenUserInfoSchema,
    ) -> list[ResultAnswersResponseSchema]:
        if not await self._admin_or_owner(uow, user_info, company_id):
            raise NotOwnerOrAdminPermissionException

        results = await uow.quiz_results.get_company_quiz_results(company_id, quiz_id)
        data = [self._map_result(result) for result in results]
        return data

    async def export_company_quiz_results(
        self,
        uow: UnitOfWork,
        company_id: int,
        quiz_id: int,
        user: TokenUserInfoSchema,
        export_type: ExportType,
    ):
        if not await self._admin_or_owner(uow, user, company_id):
            raise NotOwnerOrAdminPermissionException

        results = await uow.quiz_results.get_company_quiz_results(company_id, quiz_id)
        data = [
            CompanyExportQuizResultsSchema(
                user_email=res.user.email,
                company_name=res.company.name,
                quiz_title=res.quiz.title,
                total_questions=res.total_questions,
                answered_questions=res.answered_questions,
                correct_answers=res.correct_answers,
            )
            for res in results
        ]

        if export_type == ExportType.csv:
            return data_manager.export_to_csv(
                data, filename=f"quiz_{quiz_id}_results.csv"
            )

        return data_manager.export_to_json(
            data, filename=f"quiz_{quiz_id}_results.json"
        )

    async def create_from_import_data(
        self,
        uow: UnitOfWork,
        company_id: int,
        quiz_file: UploadFile,
        user: TokenUserInfoSchema,
    ) -> ResponseSchema:
        excel_quizzes = data_manager.parse_excel_data(quiz_file)
        existing_quizzes = await uow.quizzes.get_by_titles(
            [quiz["title"] for quiz in excel_quizzes]
        )
        quiz_map = {q.title: q for q in existing_quizzes}

        to_update = []
        to_create = []

        for quiz_data in excel_quizzes:
            existing = quiz_map.get(quiz_data["title"])
            if existing:
                to_update.append((existing.id, existing))
            else:
                to_create.append(quiz_data)

        for quiz_id, quiz_data in to_update:
            logger.info(quiz_data)
            data = QuizUpdateSchema.model_validate(quiz_data)
            await self.upsert_quiz(uow, company_id, data, user, quiz_id)

        if to_create:
            new_quizzes = await uow.quizzes.create_many(
                [
                    {
                        **QuizCreateSchema(**quiz).model_dump(exclude={"questions"}),
                        "company_id": company_id,
                    }
                    for quiz in to_create
                ]
            )
            await uow.session.flush()

            all_questions = [
                {
                    **QuestionCreateSchema(**question).model_dump(exclude={"answers"}),
                    "quiz_id": created.id,
                }
                for quiz, created in zip(to_create, new_quizzes)
                for question in quiz["questions"]
            ]

            created_questions = await uow.questions.create_many(all_questions)
            await uow.session.flush()

            all_answers = []
            question_iter = iter(created_questions)

            for quiz in to_create:
                for question in quiz["questions"]:
                    created_question = next(question_iter)
                    for ans in question["answers"]:
                        all_answers.append({**ans, "question_id": created_question.id})

            await uow.answers.create_many(all_answers)

        return ResponseSchema(
            msg="Your has been imported and created. You can check on your quiz profile"
        )
