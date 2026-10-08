from __future__ import annotations

from typing import Any, Dict

from .base_agent import BaseAgent


class InterviewAgent(BaseAgent):
    def generate_question(self, analysis: Dict[str, Any], previous_question: str = "", previous_answer: str = "") -> str:
        if previous_answer:
            prompt = f"""
You are the Interviewer Agent.

The candidate previously answered this question:
{previous_question}

Their answer:
{previous_answer}

Based on the resume and job analysis summary below, generate a single focused follow-up interview question.

Job Analysis:
{analysis}

Return only the next interview question.
"""
        else:
            prompt = f"""
You are the Interviewer Agent.

Generate ONE highly tailored interview question for the candidate based on the following analysis.

Job Analysis:
{analysis}

The question should connect the candidate's background to the role requirements.
Return only the interview question.
"""
        try:
            question = self._run(prompt)
            if question:
                return question
        except Exception as exc:
            print("Question generation error:", exc)

        return (
            "Tell me about yourself and explain how your experience connects to this role and the requirements in the job description."
        )
