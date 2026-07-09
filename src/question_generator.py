import json
import random
from src.llm_client import ollama_client
from src.question_repository import repository
from src.models import Track, Level, Question

def build_generation_prompt(track: Track, level: Level, count: int, seed_questions: list[Question]) -> str:
    prompt = f"Gere {count} novas questões de múltipla escolha sobre o assunto {track.value} e nível {level.value}.\n"
    if seed_questions:
        prompt += "Baseie-se nos seguintes exemplos:\n"
        for q in seed_questions:
            prompt += f"- {q.text}\n"
            for alt in q.alternatives:
                prompt += f"  {alt.id}: {alt.text} (correta? {alt.is_correct})\n"
    prompt += """
As novas questões devem ser no mesmo estilo, com 4 alternativas (a, b, c, d) e uma resposta correta.
Retorne apenas um JSON com a lista de questões, cada uma com campos: text, track, level, has_answer (true), has_multiple_answers (false), alternatives (lista de objetos com text e is_correct).
Não inclua comentários.
"""
    return prompt

def generate_questions(track: Track, level: Level, count: int = 5, seed_ids: list[int] = None) -> list:
    seed_questions = []
    if seed_ids:
        for sid in seed_ids:
            q = repository.get_by_id(sid)
            if q:
                seed_questions.append(q)
    if not seed_questions:
        all_q = repository.get_by_track_level(track.value, level.value)
        seed_questions = random.sample(all_q, min(3, len(all_q)))

    prompt = build_generation_prompt(track, level, count, seed_questions)
    response = ollama_client.generate(prompt)

    try:
        import re
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            data = json.loads(json_str)
            return data
        else:
            data = json.loads(response)
            return data
    except Exception:
        return {"error": "Failed to parse JSON", "raw": response}

    return []