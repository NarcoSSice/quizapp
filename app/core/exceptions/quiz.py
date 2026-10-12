from fastapi import HTTPException


class QuizNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Quiz not found")


class CorrectAnswersException(ValueError):
    def __init__(self):
        super().__init__("Question must have at least one correct answer")


class ReadingExcelError(HTTPException):
    def __init__(self, error: ValueError):
        super().__init__(status_code=400, detail=f"Error reading Excel: {str(error)}")
