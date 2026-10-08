from __future__ import annotations

import json
from typing import Any, Dict

from .base_agent import BaseAgent
from questions import FALLBACK_QUESTIONS, FINAL_CANDIDATE_QUESTION, TAILORED_QUESTION_COUNT


class JobAnalysisAgent(BaseAgent):
    def analyze(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        prompt = f"""
You are the Resume & Job Analysis Agent.

Analyze the candidate resume and target job description.

Return only a valid JSON object with these keys: candidate_profile, required_skills, matching_skills, skill_gaps, strengths, role_summary, and interview_questions.

The interview_questions value must be an array of exactly {TAILORED_QUESTION_COUNT} distinct questions tailored to both documents, including role-specific, behavioral, and experience questions. Do not add the candidate's closing question; the application appends it from the question bank.

Resume:
{resume_text[:4000]}

Job Description:
{job_description[:4000]}
"""

        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                text={"format": {"type": "json_object"}},
            )
            analysis = json.loads(response.output_text)
            questions = analysis.get("interview_questions", [])
            if not isinstance(questions, list):
                raise ValueError("interview_questions must be a list")

            questions = [item.strip() for item in questions if isinstance(item, str) and item.strip()]
            if len(questions) != TAILORED_QUESTION_COUNT:
                raise ValueError(f"Job analysis must return exactly {TAILORED_QUESTION_COUNT} tailored interview questions")

            analysis["interview_questions"] = questions + [FINAL_CANDIDATE_QUESTION]
            return analysis
        except Exception as exc:
            print("Job analysis error:", exc)
            return {
                "candidate_profile": "Unable to analyze resume.",
                "required_skills": [],
                "matching_skills": [],
                "skill_gaps": [],
                "strengths": [],
                "role_summary": "Analysis failed.",
                "interview_questions": FALLBACK_QUESTIONS + [FINAL_CANDIDATE_QUESTION],
            }
