import csv
import io
import json

import pandas as pd
from fastapi import UploadFile
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from core.exceptions.quiz import ReadingExcelError


class ExportImportManager:
    @staticmethod
    def export_to_csv(results: list[BaseModel], filename: str) -> StreamingResponse:
        fieldnames = list(results[0].model_fields.keys())

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)

        writer.writeheader()
        for result in results:
            writer.writerow(result.model_dump())

        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    @staticmethod
    def export_to_json(data: list[BaseModel], filename: str) -> StreamingResponse:
        json_str = json.dumps(
            [item.model_dump() for item in data], ensure_ascii=False, indent=2
        )
        output = io.BytesIO(json_str.encode("utf-8"))

        return StreamingResponse(
            output,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @staticmethod
    def parse_excel_data(file: UploadFile) -> list[dict]:
        try:
            data = pd.read_excel(file.file)
        except ValueError as error:
            raise ReadingExcelError(error)

        quizzes = []
        for (quiz_title, quiz_description), quiz_group in data.groupby(
            ["quiz_title", "quiz_description"]
        ):
            quiz_data = {
                "title": quiz_title,
                "description": quiz_description,
                "questions": [],
            }
            for question_title, question_group in quiz_group.groupby("question_title"):
                question_data = {"title": question_title, "answers": []}
                for _, row in question_group.iterrows():
                    question_data["answers"].append(
                        {
                            "text": row["answer_text"],
                            "is_correct": bool(row["is_correct"]),
                        }
                    )
                quiz_data["questions"].append(question_data)
            quizzes.append(quiz_data)
        return quizzes


data_manager = ExportImportManager()
