from src.llm_client import ollama_client
from src.question_repository import repository
from src.models import Question

def build_question_prompt(question: Question) -> str:
    prompt = f"Questão: {question.text}\n"
    if question.alternatives:
        prompt += "Alternativas:\n"
        for alt in question.alternatives:
            prompt += f"{alt.id}: {alt.text}\n"
    prompt += "\nForneça a resposta correta (número da alternativa) e uma explicação detalhada."
    return prompt

def explain_question(question_id: int) -> dict:
    q = repository.get_by_id(question_id)
    if not q:
        return {"error": "Question not found"}

    prompt = build_question_prompt(q)
    response = ollama_client.generate(prompt)

    return {
        "question_id": q.id,
        "text": q.text,
        "explanation": response,
        "answer": extract_answer(response)
    }

def extract_answer(text: str) -> str:
    import re
    match = re.search(r'(?:alternativa|resposta)\s*[:\-]?\s*([a-dA-D])', text)
    if match:
        return match.group(1).lower()
    match = re.search(r'\b([a-dA-D])\b', text)
    if match:
        return match.group(1).lower()
    return ""

def generate_answers_for_questions(track: str = None, level: str = None, limit: int = 10) -> list:
    questions = repository.get_by_track_level(track, level)
    results = []
    for q in questions[:limit]:
        explanation = explain_question(q.id)
        results.append(explanation)
    return results