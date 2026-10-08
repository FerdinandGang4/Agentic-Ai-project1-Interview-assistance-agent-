from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .evaluation_agent import EvaluationAgent
from .interview_agent import InterviewAgent
from .job_analysis_agent import JobAnalysisAgent
from .base_agent import BaseAgent
from questions import COMPLETION_MESSAGE, OPENING_QUESTION


@dataclass
class InterviewSession:
    resume_text: str = ""
    job_description: str = ""
    analysis: Dict[str, Any] = field(default_factory=dict)
    interview_questions: List[str] = field(default_factory=list)
    current_question: str = ""
    previous_questions: List[str] = field(default_factory=list)
    answered_questions: List[str] = field(default_factory=list)
    answers: List[str] = field(default_factory=list)
    feedback_history: List[str] = field(default_factory=list)


class InterviewManagerAgent(BaseAgent):
    def __init__(self, client, model: str = "gpt-4o-mini"):
        super().__init__(client, model)
        self.job_analysis_agent = JobAnalysisAgent(client, model)
        self.interview_agent = InterviewAgent(client, model)
        self.evaluation_agent = EvaluationAgent(client, model)
        self.session = InterviewSession()

    def reset(self) -> None:
        self.session = InterviewSession()

    def start(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        self.session = InterviewSession(
            resume_text=resume_text,
            job_description=job_description,
        )
        self.session.analysis = self.job_analysis_agent.analyze(resume_text, job_description)
        self.session.interview_questions = [OPENING_QUESTION] + self.session.analysis["interview_questions"]
        self.session.current_question = self.interview_agent.next_question(
            self.session.interview_questions,
            answers_received=0,
        )
        self.session.previous_questions.append(self.session.current_question)
        return {
            "analysis": self.session.analysis,
            "question": self.session.current_question,
            "questions": self.session.interview_questions,
            "history": self.session.previous_questions,
        }

    def evaluate_answer(self, question: str, answer: str) -> Dict[str, Any]:
        if not answer or not answer.strip():
            return {
                "feedback": "Please record and submit your answer first.",
                "question": self.session.current_question,
                "completed": False,
                "accepted": False,
                "answers_received": len(self.session.answers),
            }

        if not self.session.interview_questions:
            return {
                "feedback": "Start an interview before submitting an answer.",
                "question": "",
                "completed": False,
                "accepted": False,
                "answers_received": 0,
            }

        if len(self.session.answers) >= len(self.session.interview_questions):
            return {
                "question": self.session.current_question,
                "feedback": self.session.feedback_history[-1] if self.session.feedback_history else "",
                "completed": True,
                "accepted": False,
                "answers_received": len(self.session.answers),
            }

        expected_question = self.session.interview_questions[len(self.session.answers)]
        if question != expected_question:
            return {
                "question": expected_question,
                "feedback": "This answer does not match the current interview question. Please answer the displayed question.",
                "completed": False,
                "accepted": False,
                "answers_received": len(self.session.answers),
            }

        self.session.answered_questions.append(question)
        self.session.answers.append(answer.strip())

        if len(self.session.answers) < len(self.session.interview_questions):
            next_question = self.interview_agent.next_question(
                self.session.interview_questions,
                answers_received=len(self.session.answers),
            )
            self.session.current_question = next_question
            self.session.previous_questions.append(next_question)
            return {
                "question": next_question,
                "feedback": "",
                "completed": False,
                "accepted": True,
                "answers_received": len(self.session.answers),
            }

        evaluation = self.evaluation_agent.evaluate_interview(
            self.session.answered_questions,
            self.session.answers,
            self.session.analysis,
        )
        self.session.feedback_history.append(evaluation["feedback"])
        self.session.current_question = COMPLETION_MESSAGE

        return {
            "question": self.session.current_question,
            "feedback": evaluation["feedback"],
            "evaluation": evaluation,
            "completed": True,
            "accepted": True,
            "answers_received": len(self.session.answers),
        }

    def final_summary(self) -> str:
        if not self.session.feedback_history:
            return "No evaluation recorded yet."
        return self.session.feedback_history[-1]
