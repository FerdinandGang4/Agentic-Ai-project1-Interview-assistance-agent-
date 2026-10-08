from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .evaluation_agent import EvaluationAgent
from .interview_agent import InterviewAgent
from .job_analysis_agent import JobAnalysisAgent
from .base_agent import BaseAgent


@dataclass
class InterviewSession:
    resume_text: str = ""
    job_description: str = ""
    analysis: Dict[str, Any] = field(default_factory=dict)
    current_question: str = ""
    previous_questions: List[str] = field(default_factory=list)
    answers: List[str] = field(default_factory=list)
    feedback_history: List[str] = field(default_factory=list)


class InterviewManagerAgent(BaseAgent):
    def __init__(self, client, model: str = "gpt-4o-mini"):
        super().__init__(client, model)
        self.job_analysis_agent = JobAnalysisAgent(client, model)
        self.interview_agent = InterviewAgent(client, model)
        self.evaluation_agent = EvaluationAgent(client, model)
        self.session = InterviewSession()

    def start(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        self.session = InterviewSession(
            resume_text=resume_text,
            job_description=job_description,
        )
        self.session.analysis = self.job_analysis_agent.analyze(resume_text, job_description)
        self.session.current_question = self.interview_agent.generate_question(self.session.analysis)
        self.session.previous_questions.append(self.session.current_question)
        return {
            "analysis": self.session.analysis,
            "question": self.session.current_question,
            "history": self.session.previous_questions,
        }

    def evaluate_answer(self, question: str, answer: str) -> Dict[str, Any]:
        if not answer or not answer.strip():
            return {"feedback": "Please record and submit your answer first."}

        evaluation = self.evaluation_agent.evaluate(question, answer, self.session.analysis)
        self.session.answers.append(answer)
        self.session.feedback_history.append(evaluation["feedback"])

        follow_up = self.interview_agent.generate_question(
            self.session.analysis,
            previous_question=question,
            previous_answer=answer,
        )
        self.session.current_question = follow_up
        self.session.previous_questions.append(follow_up)

        return {
            "question": follow_up,
            "feedback": evaluation["feedback"],
            "evaluation": evaluation,
        }

    def final_summary(self) -> str:
        if not self.session.feedback_history:
            return "No evaluation recorded yet."
        return "\n\n".join(self.session.feedback_history[-3:])
