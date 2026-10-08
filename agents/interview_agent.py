from __future__ import annotations

from typing import List

from .base_agent import BaseAgent


class InterviewAgent(BaseAgent):
    def next_question(self, questions: List[str], answers_received: int) -> str:
        if answers_received >= len(questions):
            return "Interview complete. Your feedback is ready."
        return questions[answers_received]
