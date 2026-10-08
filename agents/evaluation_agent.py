from __future__ import annotations

from typing import Any, Dict

from .base_agent import BaseAgent


class EvaluationAgent(BaseAgent):
    def evaluate(self, question: str, answer: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
You are the Evaluation Agent.

Evaluate the candidate answer using this rubric:
1. Relevance to the question and the job
2. Clarity and structure
3. Technical quality and completeness
4. Communication quality
5. Strengths and areas to improve

Question:
{question}

Candidate Answer:
{answer}

Job Analysis:
{analysis}

Return a concise response with these sections:
- overall_score
- strengths
- improvements
- feedback
- improved_answer

Keep it practical and useful.
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
