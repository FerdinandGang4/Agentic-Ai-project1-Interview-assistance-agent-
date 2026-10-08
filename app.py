import os
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file.")

client = OpenAI(api_key=api_key)


class BaseAgent:
    def __init__(self, client: OpenAI, model: str = "gpt-4o-mini"):
        self.client = client
        self.model = model

    def _run(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )
        return response.output_text.strip()


class JobAnalysisAgent(BaseAgent):
    def analyze(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        prompt = f"""
You are the Resume & Job Analysis Agent.

Analyze the candidate resume and the target job description.

Return a concise but useful JSON object with these keys:
- candidate_profile
- required_skills
- matching_skills
- skill_gaps
- strengths
- role_summary

Resume:
{resume_text[:4000]}

Job Description:
{job_description[:4000]}

Return only valid JSON.
"""
        try:
            result = self._run(prompt)
            import json

            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return {
                    "candidate_profile": result,
                    "required_skills": [],
                    "matching_skills": [],
                    "skill_gaps": [],
                    "strengths": [],
                    "role_summary": result[:500],
                }
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
    def __init__(self, client: OpenAI, model: str = "gpt-4o-mini"):
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


def read_uploaded_text(file_path):
    if not file_path:
        return ""

    file_path = str(file_path)
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        if ext == ".pdf":
            try:
                from pypdf import PdfReader
            except ImportError as exc:
                raise RuntimeError("Missing dependency: install with 'pip install pypdf'") from exc

            reader = PdfReader(file_path)
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages)

        if ext == ".docx":
            try:
                from docx import Document
            except ImportError as exc:
                raise RuntimeError("Missing dependency: install with 'pip install python-docx'") from exc

            doc = Document(file_path)
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)

        return ""

    except Exception as exc:
        raise ValueError(
            f"Could not read uploaded file: {os.path.basename(file_path)}. Please upload a .txt, .pdf, or .docx file."
        ) from exc


def text_to_speech(text):
    try:
        audio_file = os.path.abspath(f"question_{uuid.uuid4().hex}.mp3")
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text,
        ) as response:
            response.stream_to_file(audio_file)
        return audio_file
    except Exception as exc:
        print("TTS Error:", exc)
        return None


def transcribe_audio(audio_file):
    if audio_file is None:
        return None

    try:
        with open(audio_file, "rb") as audio:
            transcription = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio,
            )
        return transcription.text
    except Exception as exc:
        print("Transcription Error:", exc)
        return None


session_manager = InterviewManagerAgent(client)


def start_interview(resume_file, job_description_file):
    if resume_file is None:
        return "Please upload your resume.", None, "❌ Resume missing"

    if job_description_file is None:
        return "Please upload the job description.", None, "❌ Job description missing"

    try:
        resume_text = read_uploaded_text(resume_file)
        job_description = read_uploaded_text(job_description_file)
    except ValueError as exc:
        return str(exc), None, "❌ File read error"

    if not resume_text.strip() or not job_description.strip():
        return (
            "The uploaded files are empty or unreadable. Please upload valid text, PDF, or DOCX files.",
            None,
            "❌ Empty files",
        )

    state = session_manager.start(resume_text, job_description)
    question = state["question"]
    audio = text_to_speech(question)
    return question, audio, "🟢 Interview started"


def submit_answer(audio_file):
    if audio_file is None:
        return "", "❌ Record your answer first."

    transcript = transcribe_audio(audio_file)
    if transcript is None:
        return "", "❌ Could not transcribe recording."

    return transcript, "✅ Answer received"


def get_feedback(question, answer):
    if not answer or not answer.strip():
        return "Please record and submit your answer first.", "❌ No answer available"

    result = session_manager.evaluate_answer(question, answer)
    feedback = result.get("feedback", "Unable to generate feedback.")
    return feedback, "⭐ Feedback generated"


css = """
.gradio-container {
    max-width: 1150px !important;
    margin: auto !important;
    padding: 6px !important;
}

h1 {
    font-size: 24px !important;
    margin: 2px !important;
}

h2 {
    font-size: 17px !important;
    margin: 2px !important;
}

footer {
    display: none !important;
}
"""


with gr.Blocks(title="AI Interview Coach") as demo:
    gr.Markdown(
        """
        # 🎤 AI Interview Coach
        **Upload → Start → Listen → Record → Submit → Feedback**
        """
    )

    with gr.Row():
        resume_file = gr.File(
            label="📄 Resume",
            file_types=[".pdf", ".docx", ".txt"],
            type="filepath",
            height=65,
        )
        jd_file = gr.File(
            label="📋 Job Description",
            file_types=[".pdf", ".docx", ".txt"],
            type="filepath",
            height=65,
        )
        start_button = gr.Button("▶ Start Interview", variant="primary")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## 🤖 Interviewer")
            question_output = gr.Textbox(
                label="Question",
                lines=2,
                max_lines=3,
                interactive=False,
            )
            question_voice = gr.Audio(
                label="🔊 Question Audio",
                autoplay=True,
                interactive=False,
            )

        with gr.Column(scale=1):
            gr.Markdown("## 🎙️ Your Answer")
            voice_input = gr.Audio(
                sources=["microphone"],
                type="filepath",
                label="Record Answer",
            )
            submit_button = gr.Button("✅ Submit Answer", variant="primary")

    with gr.Row():
        transcript_output = gr.Textbox(
            label="📝 Your Answer",
            lines=2,
            max_lines=3,
            interactive=False,
        )
        status_output = gr.Textbox(
            label="Status",
            lines=1,
            interactive=False,
        )

    feedback_button = gr.Button("⭐ Get Interview Feedback", variant="secondary")
    feedback_output = gr.Textbox(
        label="🧠 AI Coach Feedback",
        placeholder="Your interview feedback will appear here...",
        lines=5,
        max_lines=7,
        interactive=False,
    )

    start_button.click(
        fn=start_interview,
        inputs=[resume_file, jd_file],
        outputs=[question_output, question_voice, status_output],
    )

    submit_button.click(
        fn=submit_answer,
        inputs=[voice_input],
        outputs=[transcript_output, status_output],
    )

    feedback_button.click(
        fn=get_feedback,
        inputs=[question_output, transcript_output],
        outputs=[feedback_output, status_output],
    )


if __name__ == "__main__":
    demo.launch(inbrowser=True, css=css)
