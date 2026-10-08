import os
import uuid

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

from agents.interview_manager_agent import InterviewManagerAgent


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file.")

client = OpenAI(api_key=api_key)
session_manager = InterviewManagerAgent(client)


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
        return "Please record and submit your answer first.", "❌ No answer available", question, None

    result = session_manager.evaluate_answer(question, answer)
    feedback = result.get("feedback", "Unable to generate feedback.")
    next_question = result.get("question", question)
    next_audio = text_to_speech(next_question) if next_question != question else None
    return feedback, "⭐ Feedback generated", next_question, next_audio


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
        outputs=[feedback_output, status_output, question_output, question_voice],
    )


if __name__ == "__main__":
    demo.launch(inbrowser=True, css=css)
