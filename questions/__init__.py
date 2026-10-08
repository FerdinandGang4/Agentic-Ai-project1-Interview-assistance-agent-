from __future__ import annotations

import json
from pathlib import Path


_bank_path = Path(__file__).with_name("question_bank.json")
with _bank_path.open(encoding="utf-8") as _bank_file:
    QUESTION_BANK = json.load(_bank_file)

TAILORED_QUESTION_COUNT = QUESTION_BANK["tailored_question_count"]
OPENING_QUESTION = QUESTION_BANK["opening_question"]
FINAL_CANDIDATE_QUESTION = QUESTION_BANK["final_candidate_question"]
FALLBACK_QUESTIONS = QUESTION_BANK["fallback_questions"]
COMPLETION_MESSAGE = QUESTION_BANK["completion_message"]
TOTAL_QUESTION_COUNT = TAILORED_QUESTION_COUNT + 2

if len(FALLBACK_QUESTIONS) != TAILORED_QUESTION_COUNT:
    raise ValueError("Question bank fallback count does not match tailored question count")
if not OPENING_QUESTION.strip() or not FINAL_CANDIDATE_QUESTION.strip():
    raise ValueError("Question bank opening and closing questions must not be empty")
