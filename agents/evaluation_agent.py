from __future__ import annotations

from typing import Any, Dict, List

from .base_agent import BaseAgent


class EvaluationAgent(BaseAgent):
    def evaluate(self, question: str, answer: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        return self.evaluate_interview([question], [answer], analysis)

    def evaluate_interview(
        self,
        questions: List[str],
        answers: List[str],
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        transcript = "\n\n".join(
            f"Question {index}: {question}\nCandidate answer: {answer}"
            for index, (question, answer) in enumerate(zip(questions, answers), start=1)
        )
        prompt = f"""
You are the Evaluation Agent.

Evaluate the candidate's complete interview using this rubric:
1. Relevance to the question and the job
2. Clarity and structure
3. Technical quality and completeness
4. Communication quality
5. Consistency and evidence across answers

Interview questions and answers:
{transcript}

Job Analysis:
{analysis}

Return concise overall feedback, a score, strengths, improvement areas, and one prioritized recommendation. Include brief notes for individual answers where useful.

Keep it practical and base conclusions on all answers together.
"""
        try:
            result = self._run(prompt)
            return {
                "feedback": result,
                "overall_score": "N/A",
                "strengths": [],
                "improvements": [],
            }
        except Exception as exc:
            print("Evaluation error:", exc)
            return {
                "feedback": "Unable to generate evaluation for this answer.",
                "overall_score": "N/A",
                "strengths": [],
                "improvements": [],
            }
