from __future__ import annotations

from typing import List

from .base_agent import BaseAgent
from questions import COMPLETION_MESSAGE


class InterviewAgent(BaseAgent):
    def next_question(self, questions: List[str], answers_received: int) -> str:
        if answers_received >= len(questions):
            return COMPLETION_MESSAGE
        return questions[answers_received]
