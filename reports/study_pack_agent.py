"""Generate expected interview Q&A with model answers and concept notes."""

from __future__ import annotations

import json
from typing import Any

from openai import OpenAI


class StudyPackAgent:
    def __init__(self, client: OpenAI, model: str = "gpt-4o-mini"):
        self.client = client
        self.model = model

    def generate(
        self,
        analysis: dict[str, Any],
        resume_text: str,
        job_description: str,
        interview_questions: list[str] | None = None,
    ) -> list[dict[str, str]]:
        known = interview_questions or analysis.get("interview_questions") or []
        known_block = "\n".join(f"- {q}" for q in known[:8]) or "- (none yet)"

        prompt = f"""
You are an interview coach preparing a study pack for a candidate.

Using the resume, job description, and analysis, create a JSON object with key "items".
"items" must be an array of 6 to 8 objects. Each object must have:
- question: a realistic interview question for this role
- model_answer: a strong, concise spoken-style answer (8-14 sentences max)
- concept_explanation: clear explanation of the underlying concept/skill and why interviewers ask it

Prefer including questions similar to these when relevant:
{known_block}

Cover a mix of technical, behavioral, and role-fit topics. Do not invent employer-specific confidential info.

Candidate analysis:
{json.dumps(analysis, default=str)[:3500]}

Resume excerpt:
{resume_text[:2500]}

Job description excerpt:
{job_description[:2500]}
"""
        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                text={"format": {"type": "json_object"}},
            )
            payload = json.loads(response.output_text)
            items = payload.get("items", [])
            cleaned: list[dict[str, str]] = []
            for item in items:
                if not isinstance(item, dict):
                    continue
                question = str(item.get("question", "")).strip()
                answer = str(item.get("model_answer", "")).strip()
                concept = str(item.get("concept_explanation", "")).strip()
                if question and answer and concept:
                    cleaned.append(
                        {
                            "question": question,
                            "model_answer": answer,
                            "concept_explanation": concept,
                        }
                    )
            return cleaned
        except Exception as exc:
            print("Study pack generation error:", exc)
            return []
