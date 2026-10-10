import os
import uuid
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

from agents.interview_manager_agent import InterviewManagerAgent
from auth import (
    build_auth_panel,
    build_header,
    handle_login,
    handle_logout,
    handle_register,
)
from library import (
    delete_document,
    get_document_path,
    save_conversation,
    save_document,
)
from library.helpers import (
    audio_choices_for_conversation,
    conversation_choices,
    document_choices,
    library_dropdowns,
    render_conversation_preview,
    user_key,
)
from questions import TOTAL_QUESTION_COUNT
from reports import build_feedback_report, build_study_pack
from ui import APP_CSS, build_interview_workspace


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
                raise RuntimeError("Missing dependency: install with 'uv add pypdf'") from exc

            reader = PdfReader(file_path)
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages)

        if ext == ".docx":
            try:
                from docx import Document
            except ImportError as exc:
                raise RuntimeError("Missing dependency: install with 'uv add python-docx'") from exc

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


def _empty_downloads():
    return None, None, ""


def _empty_history():
    return (
        "<div class='history-preview muted'>Select a past interview to read answers.</div>",
        gr.update(choices=[], value=None),
        None,
    )


def _resolve_document(user, upload_path, selected_id, kind: str, auto_save: bool):
    email = user_key(user)
    name = ""
    path = None

    if upload_path:
        path = Path(upload_path)
        name = path.name
        if auto_save and email:
            try:
                item = save_document(email, kind, path, display_name=name)
                name = item["name"]
            except Exception as exc:
                print(f"Auto-save {kind} failed:", exc)
        return str(path), name

    if selected_id and email:
        saved = get_document_path(email, kind, selected_id)
        if saved and saved.exists():
            # recover display name from choices index
            for label, value in document_choices(email, kind):
                if value == selected_id:
                    name = label.split("  ·  ")[0]
                    break
            return str(saved), name or saved.name

    return None, ""


def start_interview(user, resume_file, job_description_file, saved_resume, saved_jd, auto_save):
    if not user:
        return (
            "Please log in first.",
            None,
            "❌ Not signed in",
            "",
            None,
            "",
            *_empty_downloads(),
            *library_dropdowns(user)[:3],
            "",
        )

    resume_path, resume_name = _resolve_document(
        user, resume_file, saved_resume, "resume", bool(auto_save)
    )
    jd_path, jd_name = _resolve_document(
        user, job_description_file, saved_jd, "job", bool(auto_save)
    )

    if not resume_path:
        return (
            "Choose a saved resume or upload a new one.",
            None,
            "❌ Resume missing",
            "",
            None,
            "",
            *_empty_downloads(),
            *library_dropdowns(user)[:3],
            "Select or upload a resume.",
        )

    if not jd_path:
        return (
            "Choose a saved job description or upload a new one.",
            None,
            "❌ Job description missing",
            "",
            None,
            "",
            *_empty_downloads(),
            *library_dropdowns(user)[:3],
            "Select or upload a job description.",
        )

    try:
        resume_text = read_uploaded_text(resume_path)
        job_description = read_uploaded_text(jd_path)
    except ValueError as exc:
        return (
            str(exc),
            None,
            "❌ File read error",
            "",
            None,
            "",
            *_empty_downloads(),
            *library_dropdowns(user)[:3],
            str(exc),
        )

    if not resume_text.strip() or not job_description.strip():
        return (
            "The selected files are empty or unreadable.",
            None,
            "❌ Empty files",
            "",
            None,
            "",
            *_empty_downloads(),
            *library_dropdowns(user)[:3],
            "Files were empty.",
        )

    state = session_manager.start(
        resume_text,
        job_description,
        resume_name=resume_name,
        job_name=jd_name,
    )
    resumes, jobs, history = library_dropdowns(user)[:3]

    if state.get("blocked"):
        reason = state.get("reason") or "Documents blocked by input guardrails."
        return (
            "",
            None,
            f"🛡️ Input guardrail blocked start: {reason}",
            "",
            None,
            "",
            *_empty_downloads(),
            resumes,
            jobs,
            history,
            f"❌ {reason}",
        )

    question = state["question"]
    audio = text_to_speech(question)
    session_manager.record_question_audio(audio)
    name = user.get("name", "Candidate")
    return (
        question,
        audio,
        f"🟢 Guardrails passed · Started for {name} — Q1/{TOTAL_QUESTION_COUNT}. Using {resume_name or 'resume'} + {jd_name or 'JD'}.",
        "",
        None,
        "",
        *_empty_downloads(),
        resumes,
        jobs,
        history,
        "✅ Library updated. Input guardrails passed.",
    )


def reset_interview(user=None):
    session_manager.reset()
    lib = library_dropdowns(user)
    return (
        None,  # resume upload
        None,  # jd upload
        "",  # question
        None,  # question audio
        "Ready for a new interview.",
        "",  # transcript
        None,  # mic
        "",  # feedback
        None,  # feedback file
        None,  # study file
        "",  # download status
        lib[0],  # saved resumes
        lib[1],  # saved jds
        lib[2],  # past interviews
        lib[3],  # history preview
        lib[4],  # history audio choices
        lib[5],  # history audio player
        "",  # library status
    )


def submit_answer(audio_file):
    if audio_file is None:
        return "", "❌ Record your answer first."

    transcript = transcribe_audio(audio_file)
    if transcript is None:
        return "", "❌ Could not transcribe recording."

    return transcript, "✅ Answer received"


def get_feedback(user, question, answer, audio_file):
    result = session_manager.evaluate_answer(question, answer)
    next_question = result.get("question", question)
    history_updates = library_dropdowns(user)[2:3]  # past conversations dropdown only

    if not result.get("accepted"):
        return (
            result.get("feedback", "Unable to save this answer."),
            "❌ Answer not saved",
            next_question,
            None,
            answer,
            audio_file,
            None,
            None,
            "",
            history_updates[0] if history_updates else gr.update(),
            "",
        )

    # Persist answer audio for this turn
    session_manager.record_answer_audio(audio_file if audio_file else None)

    answers_received = result.get("answers_received", 0)
    if result.get("completed"):
        feedback = result.get("feedback", "Unable to generate interview feedback.")
        status = (
            f"⭐ Complete — all {TOTAL_QUESTION_COUNT} answers evaluated. "
            "Conversation saved to your library."
        )
        next_audio = None
        email = user_key(user)
        if email:
            ctx = session_manager.get_report_context()
            try:
                save_conversation(
                    email,
                    questions=ctx.get("answered_questions") or [],
                    answers=ctx.get("answers") or [],
                    feedback=feedback,
                    question_audio_paths=ctx.get("question_audio_paths") or [],
                    answer_audio_paths=ctx.get("answer_audio_paths") or [],
                    resume_name=ctx.get("resume_name") or "",
                    job_name=ctx.get("job_name") or "",
                )
            except Exception as exc:
                print("Conversation save failed:", exc)
                status += " (history save failed)"
        past = library_dropdowns(user)[2]
        lib_msg = "✅ Interview saved to Past interviews."
    else:
        feedback = ""
        status = f"✅ Saved {answers_received}/{TOTAL_QUESTION_COUNT}. Next: Q{answers_received + 1}."
        next_audio = text_to_speech(next_question)
        session_manager.record_question_audio(next_audio)
        past = library_dropdowns(user)[2]
        lib_msg = ""

    return (
        feedback,
        status,
        next_question,
        next_audio,
        "",
        None,
        None,
        None,
        "",
        past,
        lib_msg,
    )


def download_feedback(user, fmt):
    if not user:
        return None, "❌ Log in first."

    ctx = session_manager.get_report_context()
    feedback = ctx.get("feedback") or ""
    if not feedback or feedback == "No evaluation recorded yet.":
        return None, "❌ Finish the interview first to download feedback."

    path = build_feedback_report(
        user=user,
        feedback=feedback,
        questions=ctx.get("answered_questions") or [],
        answers=ctx.get("answers") or [],
        fmt=(fmt or "PDF").lower(),
    )
    if not path:
        return None, "❌ Could not build the feedback file."
    return path, f"✅ Feedback ready ({fmt})."


def download_study(user, fmt):
    if not user:
        return None, "❌ Log in first."

    ctx = session_manager.get_report_context()
    if not ctx.get("analysis") and not ctx.get("resume_text"):
        return None, "❌ Start an interview first so the pack matches your documents."

    path, message = build_study_pack(
        client=client,
        user=user,
        analysis=ctx.get("analysis") or {},
        resume_text=ctx.get("resume_text") or "",
        job_description=ctx.get("job_description") or "",
        interview_questions=ctx.get("interview_questions") or [],
        fmt=(fmt or "PDF").lower(),
    )
    if not path:
        return None, f"❌ {message}"
    return path, f"✅ {message}"


def login_with_library(email, password):
    auth_result = handle_login(email, password)
    user = auth_result[0]
    return (*auth_result, *library_dropdowns(user))


def register_with_library(name, email, password):
    auth_result = handle_register(name, email, password)
    user = auth_result[0]
    return (*auth_result, *library_dropdowns(user))


def logout_and_reset():
    session_manager.reset()
    auth_result = handle_logout()
    empty_lib = library_dropdowns(None)
    interview_clear = (
        None,
        None,
        "",
        None,
        "Ready for a new interview.",
        "",
        None,
        "",
        None,
        None,
        "",
    )
    return (*auth_result, *empty_lib, *interview_clear)


def save_resume_to_library(user, resume_file):
    email = user_key(user)
    if not email:
        return gr.update(), "❌ Log in first."
    if not resume_file:
        return gr.update(choices=document_choices(email, "resume")), "❌ Choose a resume file to save."
    try:
        item = save_document(email, "resume", resume_file)
        choices = document_choices(email, "resume")
        return gr.update(choices=choices, value=item["id"]), f"✅ Saved resume: {item['name']}"
    except Exception as exc:
        return gr.update(choices=document_choices(email, "resume")), f"❌ {exc}"


def save_jd_to_library(user, jd_file):
    email = user_key(user)
    if not email:
        return gr.update(), "❌ Log in first."
    if not jd_file:
        return gr.update(choices=document_choices(email, "job")), "❌ Choose a JD file to save."
    try:
        item = save_document(email, "job", jd_file)
        choices = document_choices(email, "job")
        return gr.update(choices=choices, value=item["id"]), f"✅ Saved JD: {item['name']}"
    except Exception as exc:
        return gr.update(choices=document_choices(email, "job")), f"❌ {exc}"


def delete_resume_from_library(user, selected_id):
    email = user_key(user)
    if not email:
        return gr.update(), "❌ Log in first."
    if not selected_id:
        return gr.update(choices=document_choices(email, "resume")), "❌ Select a resume to delete."
    delete_document(email, "resume", selected_id)
    choices = document_choices(email, "resume")
    return gr.update(choices=choices, value=choices[0][1] if choices else None), "✅ Resume deleted."


def delete_jd_from_library(user, selected_id):
    email = user_key(user)
    if not email:
        return gr.update(), "❌ Log in first."
    if not selected_id:
        return gr.update(choices=document_choices(email, "job")), "❌ Select a JD to delete."
    delete_document(email, "job", selected_id)
    choices = document_choices(email, "job")
    return gr.update(choices=choices, value=choices[0][1] if choices else None), "✅ Job description deleted."


def open_past_conversation(user, conversation_id):
    email = user_key(user)
    if not email:
        return (*_empty_history(), "❌ Log in first.")
    if not conversation_id:
        return (*_empty_history(), "❌ Select a past interview.")
    preview, _, _ = render_conversation_preview(email, conversation_id)
    audio_choices = audio_choices_for_conversation(email, conversation_id)
    first_audio = audio_choices[0][1] if audio_choices else None
    return (
        preview,
        gr.update(choices=audio_choices, value=first_audio),
        first_audio,
        "✅ Conversation loaded. Pick an audio clip to listen.",
    )


def play_history_audio(audio_path):
    if not audio_path:
        return None
    return audio_path if Path(audio_path).exists() else None


with gr.Blocks(title="AI Interview Coach") as demo:
    user_state = gr.State(None)

    user_chip, logout_button = build_header()
    auth = build_auth_panel()
    interview = build_interview_workspace()

    gr.HTML(
        '<footer class="app-footer-inner"><strong>AI INTERVIEW COACH</strong><span>Career development workspace</span></footer>',
        elem_id="app-footer",
    )

    library_outputs = [
        interview["saved_resume"],
        interview["saved_jd"],
        interview["past_conversation"],
        interview["history_preview"],
        interview["history_audio_choice"],
        interview["history_audio"],
    ]

    auth_event_outputs = [
        user_state,
        user_chip,
        auth["auth_status"],
        auth["auth_section"],
        interview["workspace"],
        logout_button,
        auth["name_input"],
        auth["email_input"],
        auth["password_input"],
    ]

    interview_clear_outputs = [
        interview["resume_file"],
        interview["jd_file"],
        interview["question_output"],
        interview["question_voice"],
        interview["status_output"],
        interview["transcript_output"],
        interview["voice_input"],
        interview["feedback_output"],
        interview["feedback_file"],
        interview["study_file"],
        interview["download_status"],
    ]

    auth["login_button"].click(
        fn=login_with_library,
        inputs=[auth["email_input"], auth["password_input"]],
        outputs=[*auth_event_outputs, *library_outputs],
    )

    auth["register_button"].click(
        fn=register_with_library,
        inputs=[auth["name_input"], auth["email_input"], auth["password_input"]],
        outputs=[*auth_event_outputs, *library_outputs],
    )

    logout_button.click(
        fn=logout_and_reset,
        inputs=[],
        outputs=[*auth_event_outputs, *library_outputs, *interview_clear_outputs],
    )

    interview["save_resume_btn"].click(
        fn=save_resume_to_library,
        inputs=[user_state, interview["resume_file"]],
        outputs=[interview["saved_resume"], interview["library_status"]],
    )
    interview["save_jd_btn"].click(
        fn=save_jd_to_library,
        inputs=[user_state, interview["jd_file"]],
        outputs=[interview["saved_jd"], interview["library_status"]],
    )
    interview["delete_resume_btn"].click(
        fn=delete_resume_from_library,
        inputs=[user_state, interview["saved_resume"]],
        outputs=[interview["saved_resume"], interview["library_status"]],
    )
    interview["delete_jd_btn"].click(
        fn=delete_jd_from_library,
        inputs=[user_state, interview["saved_jd"]],
        outputs=[interview["saved_jd"], interview["library_status"]],
    )
    interview["load_history_btn"].click(
        fn=open_past_conversation,
        inputs=[user_state, interview["past_conversation"]],
        outputs=[
            interview["history_preview"],
            interview["history_audio_choice"],
            interview["history_audio"],
            interview["library_status"],
        ],
    )
    interview["history_audio_choice"].change(
        fn=play_history_audio,
        inputs=[interview["history_audio_choice"]],
        outputs=[interview["history_audio"]],
    )

    interview["start_button"].click(
        fn=start_interview,
        inputs=[
            user_state,
            interview["resume_file"],
            interview["jd_file"],
            interview["saved_resume"],
            interview["saved_jd"],
            interview["auto_save_docs"],
        ],
        outputs=[
            interview["question_output"],
            interview["question_voice"],
            interview["status_output"],
            interview["transcript_output"],
            interview["voice_input"],
            interview["feedback_output"],
            interview["feedback_file"],
            interview["study_file"],
            interview["download_status"],
            interview["saved_resume"],
            interview["saved_jd"],
            interview["past_conversation"],
            interview["library_status"],
        ],
    )

    interview["submit_button"].click(
        fn=submit_answer,
        inputs=[interview["voice_input"]],
        outputs=[interview["transcript_output"], interview["status_output"]],
    )

    interview["feedback_button"].click(
        fn=get_feedback,
        inputs=[
            user_state,
            interview["question_output"],
            interview["transcript_output"],
            interview["voice_input"],
        ],
        outputs=[
            interview["feedback_output"],
            interview["status_output"],
            interview["question_output"],
            interview["question_voice"],
            interview["transcript_output"],
            interview["voice_input"],
            interview["feedback_file"],
            interview["study_file"],
            interview["download_status"],
            interview["past_conversation"],
            interview["library_status"],
        ],
    )

    interview["download_feedback_btn"].click(
        fn=download_feedback,
        inputs=[user_state, interview["download_format"]],
        outputs=[interview["feedback_file"], interview["download_status"]],
    )

    interview["download_study_btn"].click(
        fn=download_study,
        inputs=[user_state, interview["download_format"]],
        outputs=[interview["study_file"], interview["download_status"]],
    )

    interview["reset_button"].click(
        fn=reset_interview,
        inputs=[user_state],
        outputs=[
            *interview_clear_outputs,
            interview["saved_resume"],
            interview["saved_jd"],
            interview["past_conversation"],
            interview["history_preview"],
            interview["history_audio_choice"],
            interview["history_audio"],
            interview["library_status"],
        ],
    )


if __name__ == "__main__":
    demo.launch(inbrowser=True, share=True,css=APP_CSS)
