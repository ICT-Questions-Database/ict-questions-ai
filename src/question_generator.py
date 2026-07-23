import json
import random
from src.llm_client import ollama_client
from src.question_repository import repository
from src.models import Track, Level, Question

def build_generation_prompt(track: Track, level: Level, count: int, seed_questions: list[Question], question_type: str) -> str:
    examples = []
    if question_type == "true_false":
        vf_qs = [q for q in repository.get_all() if len(q.alternatives) == 2 and any(a.text.lower() in ["verdadeiro", "true"] for a in q.alternatives)]
        examples = random.sample(vf_qs, min(2, len(vf_qs)))
    elif question_type == "multiple_choice":
        multi_qs = [q for q in repository.get_all() if sum(1 for a in q.alternatives if a.is_correct) > 1]
        examples = random.sample(multi_qs, min(2, len(multi_qs)))
    else:
        single_qs = [q for q in repository.get_all() if len(q.alternatives) > 2 and sum(1 for a in q.alternatives if a.is_correct) == 1]
        examples = random.sample(single_qs, min(2, len(single_qs)))

    prompt = f"Gere {count} novas questões do tipo '{question_type}' sobre o assunto '{track.value}' e nível '{level.value}'.\n"
    
    if question_type == "true_false":
        prompt += "Cada questão deve ser do tipo Verdadeiro ou Falso, com exatamente duas alternativas: 'Verdadeiro' e 'Falso', sendo uma correta.\n"
    elif question_type == "multiple_choice":
        prompt += "Cada questão deve ser de múltipla escolha com **mais de uma** alternativa correta. Use entre 4 e 5 alternativas no total.\n"
    else:
        prompt += "Cada questão deve ser de múltipla escolha com **apenas uma** alternativa correta. Use entre 4 e 5 alternativas.\n"

    if examples:
        prompt += "\nExemplos reais do nosso banco de questões:\n"
        for i, q in enumerate(examples[:2]):
            prompt += f"\nExemplo {i+1}:\n"
            prompt += f"Pergunta: {q.text}\n"
            for alt in q.alternatives:
                prompt += f" - {alt.text} (correta? {alt.is_correct})\n"
            prompt += f"has_multiple_answers: {q.has_multiple_answers}\n"

    prompt += f"""
Agora, gere um JSON com uma lista de {count} questões. Cada questão deve ter:
- text: string
- track: "{track.value}"
- level: "{level.value}"
- has_answer: true
- has_multiple_answers: {str(question_type == "multiple_choice").lower()}
- alternatives: lista de objetos com "text" e "is_correct" (booleano)

Para verdadeiro/falso, use apenas duas alternativas: "Verdadeiro" e "Falso".
Para múltipla escolha com uma resposta, apenas uma alternativa deve ter is_correct = true.
Para múltipla escolha com várias respostas, pelo menos duas alternativas devem ter is_correct = true.

Retorne APENAS o JSON, sem texto adicional.
"""
    return prompt

def generate_questions(track: Track, level: Level, count: int = 5, seed_ids: list[int] = None, question_type: str = "single_choice") -> list:
    seed_questions = []
    if seed_ids:
        for sid in seed_ids:
            q = repository.get_by_id(sid)
            if q:
                seed_questions.append(q)
    if not seed_questions:
        all_q = repository.get_by_track_level(track.value, level.value)
        seed_questions = random.sample(all_q, min(3, len(all_q)))

    prompt = build_generation_prompt(track, level, count, seed_questions, question_type)
    response = ollama_client.generate(prompt)

    try:
        import re
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            data = json.loads(json_str)
        else:
            data = json.loads(response)
    except Exception:
        return {"error": "Failed to parse JSON", "raw": response}

    for q in data:
        q.setdefault("has_answer", True)
        if question_type == "true_false":
            q["has_multiple_answers"] = False
        elif question_type == "multiple_choice":
            q["has_multiple_answers"] = True
        else:
            q["has_multiple_answers"] = False

    return data