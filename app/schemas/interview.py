from typing import Literal

from pydantic import BaseModel, Field


class InterviewQuestion(BaseModel):
    question: str
    intent: str
    difficulty: Literal["warm-up", "core", "deep-dive"]


class AnswerRequest(BaseModel):
    answer: str = Field(min_length=1)
