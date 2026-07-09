from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class Track(str, Enum):
    CLOUD = "cloud"
    NETWORK = "network"
    COMPUTING = "computing"

class Level(str, Enum):
    HCIA = "hcia"
    HCIP = "hcip"
    HCIE = "hcie"

class CorrectAnswerSource(BaseModel):
    id: int
    alternative_id: int
    source: str

class Alternative(BaseModel):
    id: int
    text: str
    is_correct: bool
    sources: List[CorrectAnswerSource] = []

class Question(BaseModel):
    id: int
    submitted_by: Optional[int] = None
    reviewed_by: Optional[int] = None
    text: str
    level: Level
    has_answer: bool
    has_multiple_answers: bool
    track: Track
    weight: float
    status: Optional[str] = None
    sent_at: Optional[str] = None
    reviewed_at: Optional[str] = None
    last_update: Optional[str] = None
    feedback: Optional[str] = None
    alternatives: List[Alternative] = []

class QuestionExplanationRequest(BaseModel):
    question_id: int

class GenerateAnswersRequest(BaseModel):
    track: Optional[Track] = None
    level: Optional[Level] = None
    limit: int = 10

class GenerateQuestionsRequest(BaseModel):
    track: Track
    level: Level
    count: int = 5
    seed_questions: Optional[List[int]] = None