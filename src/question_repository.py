import json
from typing import List, Optional, Dict
from pathlib import Path
from src.models import Question, Alternative, CorrectAnswerSource
from src.config import settings

class QuestionRepository:
    def __init__(self):
        self._questions: Dict[int, Question] = {}
        self._load_data()

    def _load_data(self):
        data_file = Path(settings.DATA_FILE)
        if not data_file.exists():
            raise FileNotFoundError(f"Data file not found: {data_file}")
        with open(data_file, "r", encoding="utf-8") as f:
            raw = json.load(f)

        alternatives_by_question: Dict[int, List[dict]] = {}
        sources_by_alternative: Dict[int, List[CorrectAnswerSource]] = {}

        for item in raw:
            model = item.get("model")
            if model == "yourapp.Alternative":
                alt_data = {
                    "id": item["pk"],
                    "text": item["fields"]["text"],
                    "is_correct": item["fields"]["is_correct"]
                }
                qid = item["fields"]["question"]
                alternatives_by_question.setdefault(qid, []).append(alt_data)
            elif model == "yourapp.CorrectAnswersSources":
                src = CorrectAnswerSource(
                    id=item["pk"],
                    alternative_id=item["fields"]["alternative"],
                    source=item["fields"]["source"]
                )
                sources_by_alternative.setdefault(item["fields"]["alternative"], []).append(src)
            elif model == "yourapp.Question":
                fields = item["fields"]
                q = Question(
                    id=item["pk"],
                    submitted_by=fields.get("submitted_by"),
                    reviewed_by=fields.get("reviewed_by"),
                    text=fields["text"],
                    level=fields["level"].lower(),
                    has_answer=fields["has_answer"],
                    has_multiple_answers=fields["has_multiple_answers"],
                    track=fields["track"].lower(),
                    weight=float(fields["weight"]),
                    status=fields.get("status"),
                    sent_at=fields.get("sent_at") or fields.get("approved_at"),
                    reviewed_at=fields.get("reviewed_at"),
                    last_update=fields.get("last_update"),
                    feedback=fields.get("feedback")
                )
                self._questions[q.id] = q

        for qid, alt_list in alternatives_by_question.items():
            if qid in self._questions:
                alternatives = []
                for alt_data in alt_list:
                    alt_id = alt_data["id"]
                    sources = sources_by_alternative.get(alt_id, [])
                    alt = Alternative(
                        id=alt_id,
                        text=alt_data["text"],
                        is_correct=alt_data["is_correct"],
                        sources=sources
                    )
                    alternatives.append(alt)
                self._questions[qid].alternatives = alternatives

    def get_all(self) -> List[Question]:
        return list(self._questions.values())

    def get_by_id(self, qid: int) -> Optional[Question]:
        return self._questions.get(qid)

    def get_by_track_level(self, track: Optional[str] = None, level: Optional[str] = None) -> List[Question]:
        result = list(self._questions.values())
        if track:
            result = [q for q in result if q.track.value == track.lower()]
        if level:
            result = [q for q in result if q.level.value == level.lower()]
        return result

    def get_questions_without_answer(self) -> List[Question]:
        return [q for q in self._questions.values() if not q.has_answer]

repository = QuestionRepository()