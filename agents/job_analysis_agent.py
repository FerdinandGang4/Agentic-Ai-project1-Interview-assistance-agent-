from __future__ import annotations

import json
from typing import Any, Dict

from .base_agent import BaseAgent


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
  "role_summary": "..."
}}

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
            return json.loads(response.output_text)
        except Exception as exc:
            print("Job analysis error:", exc)
            return {
                "candidate_profile": "Unable to analyze resume.",
                "required_skills": [],
                "matching_skills": [],
                "skill_gaps": [],
                "strengths": [],
                "role_summary": "Analysis failed.",
            }
