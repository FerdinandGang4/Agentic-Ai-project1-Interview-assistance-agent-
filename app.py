import os
import uuid

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

from agents.interview_manager_agent import InterviewManagerAgent
from questions import TOTAL_QUESTION_COUNT


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
        return "Please upload your resume.", None, "❌ Resume missing", "", None, ""

    if job_description_file is None:
        return "Please upload the job description.", None, "❌ Job description missing", "", None, ""

    try:
        resume_text = read_uploaded_text(resume_file)
        job_description = read_uploaded_text(job_description_file)
    except ValueError as exc:
        return str(exc), None, "❌ File read error", "", None, ""

    if not resume_text.strip() or not job_description.strip():
        return (
            "The uploaded files are empty or unreadable. Please upload valid text, PDF, or DOCX files.",
            None,
            "❌ Empty files",
            "",
            None,
            "",
        )

    state = session_manager.start(resume_text, job_description)
    question = state["question"]
    audio = text_to_speech(question)
    return question, audio, f"🟢 Interview started (Question 1 of {TOTAL_QUESTION_COUNT})", "", None, ""


def reset_interview():
    session_manager.reset()
    return None, None, "", None, "Ready for a new interview.", "", None, ""


def submit_answer(audio_file):
    if audio_file is None:
        return "", "❌ Record your answer first."

    transcript = transcribe_audio(audio_file)
    if transcript is None:
        return "", "❌ Could not transcribe recording."

    return transcript, "✅ Answer received"


def get_feedback(question, answer, audio_file):
    result = session_manager.evaluate_answer(question, answer)
    next_question = result.get("question", question)
    if not result.get("accepted"):
        return (
            result.get("feedback", "Unable to save this answer."),
            "❌ Answer not saved",
            next_question,
            None,
            answer,
            audio_file,
        )

    answers_received = result.get("answers_received", 0)
    if result.get("completed"):
        feedback = result.get("feedback", "Unable to generate interview feedback.")
        status = f"⭐ Interview complete. All {TOTAL_QUESTION_COUNT} answers were evaluated."
        next_audio = None
    else:
        feedback = ""
        status = f"✅ Answer {answers_received} of {TOTAL_QUESTION_COUNT} saved. Continue to question {answers_received + 1}."
        next_audio = text_to_speech(next_question)

    return feedback, status, next_question, next_audio, "", None


css = """
body {
    background: linear-gradient(145deg, #f4f8f6 0%, #edf3f0 58%, #f7f8f4 100%);
}

.gradio-container {
    --ink: #20332f;
    --muted: #687a75;
    --line: #d9e3df;
    --accent: #176b5c;
    box-sizing: border-box !important;
    width: 100% !important;
    max-width: none !important;
    margin: 0 !important;
    padding: 28px clamp(22px, 3vw, 56px) 36px !important;
    color: var(--ink) !important;
    font-family: "Aptos", "Trebuchet MS", sans-serif !important;
}

.gradio-container .main.fillable {
    box-sizing: border-box !important;
    max-width: none !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}

#app-header {
    background: #523873;
    border: 1px solid #523873;
    border-radius: 8px;
    margin-bottom: 24px;
    padding: 24px 26px;
}

#app-header p:first-child {
    color: #d9c9ed;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    margin: 0 0 8px;
}

#app-header p:first-child strong {
    color: inherit;
}

#app-header p:last-child {
    color: #eee8f5;
    font-size: 15px;
    line-height: 1.6;
    margin: 10px 0 0;
}

#app-header p:last-child strong {
    color: #fff;
}

#app-header h1 {
    color: #fff;
    font-family: "Aptos Display", "Trebuchet MS", sans-serif;
    font-size: 32px;
    font-weight: 650;
    line-height: 1.15;
    margin: 0;
}

#app-footer {
    margin-top: 36px;
}

.app-footer-inner {
    align-items: center;
    background: #523873;
    border-radius: 8px;
    color: #eee8f5;
    display: flex;
    font-size: 12px;
    justify-content: space-between;
    padding: 16px 20px;
}

.app-footer-inner strong {
    color: #fff;
    font-size: 11px;
    letter-spacing: 0.7px;
}

#document-section {
    border-bottom: 1px solid var(--line);
    margin-bottom: 24px;
    padding-bottom: 24px;
}

.section-heading h3,
#interviewer-column h3,
#candidate-column h3 {
    color: var(--ink);
    font-size: 17px;
    font-weight: 650;
    margin: 0 0 12px;
}

.section-heading h3 {
    color: var(--muted);
    font-size: 12px;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}

#start-interview {
    align-self: end;
    min-height: 44px;
    white-space: nowrap;
}

#reset-interview {
    min-height: 42px;
    white-space: nowrap;
}

#question-output textarea {
    background: #f2f7f4 !important;
    border: 1px solid #d2e2da !important;
    border-left: 4px solid var(--accent) !important;
    color: var(--ink) !important;
    font-size: 18px !important;
    line-height: 1.55 !important;
    min-height: 126px !important;
    padding: 18px !important;
}

#interviewer-column,
#candidate-column {
    min-width: 0;
}

#response-controls {
    align-items: end;
    margin-top: 8px;
}

#status-output textarea {
    color: var(--muted) !important;
    min-height: 42px !important;
}

#feedback-output textarea {
    background: #f7f8f4 !important;
    border-color: var(--line) !important;
    color: var(--ink) !important;
    line-height: 1.55 !important;
}

.gradio-container input,
.gradio-container textarea,
.gradio-container button {
    border-radius: 6px !important;
}

.gradio-container input:focus,
.gradio-container textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgb(23 107 92 / 14%) !important;
}

.gradio-container button.primary {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: #fff !important;
}

.gradio-container button.secondary {
    background: #e4eee9 !important;
    border-color: #d0dfd8 !important;
    color: #205d50 !important;
}

.gradio-container button:hover {
    filter: brightness(0.96);
}

footer:not(.app-footer-inner) {
    display: none !important;
}

@media (max-width: 760px) {
    .gradio-container {
        padding: 18px 16px 24px !important;
    }

    #app-header h1 {
        font-size: 27px;
    }

    #app-header p:last-child {
        font-size: 14px;
    }

    .app-footer-inner {
        align-items: flex-start;
        flex-direction: column;
        gap: 6px;
    }

    #question-output textarea {
        font-size: 16px !important;
        min-height: 112px !important;
    }

    #start-interview {
        width: 100%;
    }
}
"""


with gr.Blocks(title="AI Interview Coach") as demo:
    gr.Markdown(
        """
        **INTERVIEW WORKSPACE**

        # AI Interview Coach

        **Workflow:** Upload your resume and job description → Start interview → Answer the opening question and four tailored questions → Ask your own question → Review feedback after question six.
        """,
        elem_id="app-header",
    )

    with gr.Column(elem_id="document-section"):
        gr.Markdown("### Candidate documents", elem_classes=["section-heading"])
        with gr.Row(equal_height=True):
            resume_file = gr.File(
                label="Resume",
                file_types=[".pdf", ".docx", ".txt"],
                type="filepath",
                height=76,
                scale=1,
            )
            jd_file = gr.File(
                label="Job description",
                file_types=[".pdf", ".docx", ".txt"],
                type="filepath",
                height=76,
                scale=1,
            )
            with gr.Column(scale=0, min_width=176):
                start_button = gr.Button("Start interview", variant="primary", elem_id="start-interview")
                reset_button = gr.Button("Reset interview", variant="secondary", elem_id="reset-interview")

    with gr.Row(elem_id="interview-section", equal_height=False):
        with gr.Column(scale=3, elem_id="interviewer-column"):
            gr.Markdown("### Interviewer")
            question_output = gr.Textbox(
                label="Current question",
                lines=4,
                max_lines=5,
                interactive=False,
                elem_id="question-output",
            )
            question_voice = gr.Audio(
                label="Question audio",
                autoplay=True,
                interactive=False,
            )

        with gr.Column(scale=2, elem_id="candidate-column"):
            gr.Markdown("### Candidate response")
            voice_input = gr.Audio(
                sources=["microphone"],
                type="filepath",
                label="Record your answer",
            )
            submit_button = gr.Button("Transcribe answer", variant="primary")

    with gr.Row(elem_id="response-controls"):
        transcript_output = gr.Textbox(
            label="Transcribed answer",
            lines=2,
            max_lines=4,
            interactive=False,
            scale=3,
        )
        with gr.Column(scale=2):
            status_output = gr.Textbox(
                label="Interview status",
                lines=1,
                interactive=False,
                elem_id="status-output",
            )
            feedback_button = gr.Button("Save answer & continue", variant="secondary")
    feedback_output = gr.Textbox(
        label="Final interview feedback",
        placeholder="Final interview feedback appears after all six answers.",
        lines=5,
        max_lines=7,
        interactive=False,
        elem_id="feedback-output",
    )
    gr.HTML(
        '<footer class="app-footer-inner"><strong>AI INTERVIEW COACH</strong><span>Career development workspace</span></footer>',
        elem_id="app-footer",
    )

    start_button.click(
        fn=start_interview,
        inputs=[resume_file, jd_file],
        outputs=[question_output, question_voice, status_output, transcript_output, voice_input, feedback_output],
    )

    submit_button.click(
        fn=submit_answer,
        inputs=[voice_input],
        outputs=[transcript_output, status_output],
    )

    feedback_button.click(
        fn=get_feedback,
        inputs=[question_output, transcript_output, voice_input],
        outputs=[feedback_output, status_output, question_output, question_voice, transcript_output, voice_input],
    )

    reset_button.click(
        fn=reset_interview,
        inputs=[],
        outputs=[resume_file, jd_file, question_output, question_voice, status_output, transcript_output, voice_input, feedback_output],
    )


if __name__ == "__main__":
    demo.launch(inbrowser=True, css=css)
