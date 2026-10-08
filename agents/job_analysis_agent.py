from __future__ import annotations

import json
from typing import Any, Dict

from .base_agent import BaseAgent


FINAL_CANDIDATE_QUESTION = "Do you have any questions for us about the role, team, or interview process?"


class JobAnalysisAgent(BaseAgent):
    def analyze(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        prompt = f"""
You are the Resume & Job Analysis Agent.

Analyze the candidate resume and target job description.

Return only valid JSON with this structure:
{{
  "candidate_profile": "...",
  "required_skills": ["..."],
  "matching_skills": ["..."],
  "skill_gaps": ["..."],
  "strengths": ["..."],
    "role_summary": "...",
    "interview_questions": [
        "First tailored question...",
        "Second tailored question...",
        "Third tailored question...",
        "Fourth tailored question...",
        "Do you have any questions for us about the role, team, or interview process?"
    ]
}}

Generate exactly four distinct questions tailored to both documents, including role-specific, behavioral, and experience questions. The fifth question must ask whether the candidate has questions for the interviewer.

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
            if len(questions) != 5:
                raise ValueError("Job analysis must return exactly five interview questions")

            analysis["interview_questions"] = questions[:4] + [FINAL_CANDIDATE_QUESTION]
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
                "interview_questions": [
                    "Describe how your experience prepares you for this role.",
                    "Tell me about a challenging project relevant to this position.",
                    "How do you approach solving a difficult technical problem?",
                    "Describe a time you collaborated to achieve a work goal.",
                    FINAL_CANDIDATE_QUESTION,
                ],
            }
