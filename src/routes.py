from fastapi import APIRouter, HTTPException
from src.models import (
    GenerateAnswersRequest,
    GenerateQuestionsRequest,
)
from src.question_repository import repository
from src.explanation_service import explain_question, generate_answers_for_questions
from src.question_generator import generate_questions

router = APIRouter(prefix="/api/v1", tags=["llm"])

@router.get("/questions")
def list_questions():
    return repository.get_all()

@router.get("/questions/{qid}")
def get_question(qid: int):
    q = repository.get_by_id(qid)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return q

@router.post("/explain/{qid}")
def explain(qid: int):
    result = explain_question(qid)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.post("/generate-answers")
def generate_answers(req: GenerateAnswersRequest):
    results = generate_answers_for_questions(
        track=req.track.value if req.track else None,
        level=req.level.value if req.level else None,
        limit=req.limit
    )
    return {"results": results}

@router.post("/generate-questions")
def generate(req: GenerateQuestionsRequest):
    seed_ids = req.seed_questions or []
    new_questions = generate_questions(
        track=req.track,
        level=req.level,
        count=req.count,
        seed_ids=seed_ids,
        question_type=req.question_type
    )
    return {"generated": new_questions}