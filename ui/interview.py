"""Professional interview workspace with compact library + history."""

from __future__ import annotations

import gradio as gr


def build_interview_workspace() -> dict:
    """Build the interview UI inside a column shown after login."""
    with gr.Column(visible=False, elem_id="interview-workspace") as workspace:
        with gr.Group(elem_id="library-section", elem_classes=["panel-card"]):
            gr.Markdown("### Library · resumes, JDs & past interviews", elem_classes=["section-heading"])
            with gr.Row(equal_height=True):
                with gr.Column(scale=1, min_width=180):
                    saved_resume = gr.Dropdown(
                        label="Saved resumes",
                        choices=[],
                        value=None,
                        interactive=True,
                        elem_id="saved-resume",
                    )
                    with gr.Row():
                        save_resume_btn = gr.Button("Save upload", variant="secondary", scale=1)
                        delete_resume_btn = gr.Button("Delete", variant="secondary", scale=1)
                with gr.Column(scale=1, min_width=180):
                    saved_jd = gr.Dropdown(
                        label="Saved job descriptions",
                        choices=[],
                        value=None,
                        interactive=True,
                        elem_id="saved-jd",
                    )
                    with gr.Row():
                        save_jd_btn = gr.Button("Save upload", variant="secondary", scale=1)
                        delete_jd_btn = gr.Button("Delete", variant="secondary", scale=1)
                with gr.Column(scale=1, min_width=200):
                    past_conversation = gr.Dropdown(
                        label="Past interviews",
                        choices=[],
                        value=None,
                        interactive=True,
                        elem_id="past-conversation",
                    )
                    load_history_btn = gr.Button("Open conversation", variant="primary")

            history_preview = gr.HTML(
                "<div class='history-preview muted'>Select a past interview to read answers.</div>",
                elem_id="history-preview",
            )
            with gr.Row():
                history_audio_choice = gr.Dropdown(
                    label="Audio clip",
                    choices=[],
                    value=None,
                    interactive=True,
                    scale=2,
                    elem_id="history-audio-choice",
                )
                history_audio = gr.Audio(
                    label="Play audio",
                    interactive=False,
                    scale=2,
                    elem_id="history-audio",
                )
            library_status = gr.Textbox(
                label="Library status",
                lines=1,
                max_lines=1,
                interactive=False,
                show_label=False,
                elem_id="library-status",
                placeholder="Library actions appear here.",
            )

        with gr.Group(elem_id="document-section", elem_classes=["panel-card"]):
            gr.Markdown(
                "### 1 · Start interview  ·  upload new or reuse saved files",
                elem_classes=["section-heading"],
            )
            with gr.Row(equal_height=True):
                resume_file = gr.File(
                    label="New resume upload (optional if saved)",
                    file_types=[".pdf", ".docx", ".txt"],
                    type="filepath",
                    height=52,
                    scale=1,
                )
                jd_file = gr.File(
                    label="New JD upload (optional if saved)",
                    file_types=[".pdf", ".docx", ".txt"],
                    type="filepath",
                    height=52,
                    scale=1,
                )
                with gr.Column(scale=0, min_width=130):
                    auto_save_docs = gr.Checkbox(
                        label="Auto-save uploads",
                        value=True,
                        elem_id="auto-save-docs",
                    )
                    start_button = gr.Button(
                        "Start interview",
                        variant="primary",
                        elem_id="start-interview",
                    )
                    reset_button = gr.Button(
                        "Reset",
                        variant="secondary",
                        elem_id="reset-interview",
                    )
            status_output = gr.Textbox(
                label="Status",
                lines=1,
                max_lines=1,
                interactive=False,
                elem_id="status-output",
                show_label=False,
                placeholder="Status updates appear here.",
            )

        with gr.Group(elem_id="session-section", elem_classes=["panel-card"]):
            gr.Markdown("### 2 · Live interview", elem_classes=["section-heading"])
            with gr.Row(elem_id="interview-section", equal_height=True):
                with gr.Column(scale=3, elem_id="interviewer-column"):
                    gr.HTML('<p class="section-eyebrow">Question</p>')
                    question_output = gr.Textbox(
                        label="Current question",
                        lines=3,
                        max_lines=4,
                        interactive=False,
                        elem_id="question-output",
                        show_label=False,
                        placeholder="Your interview question will appear here after Start.",
                    )
                    question_voice = gr.Audio(
                        label="Question audio",
                        autoplay=True,
                        interactive=False,
                        elem_id="question-audio",
                    )

                with gr.Column(scale=2, elem_id="candidate-column"):
                    gr.HTML('<p class="section-eyebrow">Your answer</p>')
                    voice_input = gr.Audio(
                        sources=["microphone"],
                        type="filepath",
                        label="Microphone",
                        elem_id="voice-input",
                    )
                    with gr.Row():
                        submit_button = gr.Button("Transcribe", variant="primary", scale=1)
                        feedback_button = gr.Button(
                            "Save & continue",
                            variant="secondary",
                            scale=1,
                        )

            transcript_output = gr.Textbox(
                label="Transcript",
                lines=2,
                max_lines=3,
                interactive=False,
                elem_id="transcript-output",
                placeholder="Transcribed answer appears here.",
            )

        with gr.Group(elem_id="results-section", elem_classes=["panel-card"]):
            gr.Markdown("### 3 · Results & downloads", elem_classes=["section-heading"])
            feedback_output = gr.Textbox(
                label="Final feedback",
                placeholder="Final coaching feedback appears after all six answers.",
                lines=4,
                max_lines=6,
                interactive=False,
                elem_id="feedback-output",
            )
            with gr.Row(elem_id="download-controls"):
                download_format = gr.Radio(
                    choices=["PDF", "DOCX"],
                    value="PDF",
                    label="Format",
                    elem_id="download-format",
                    scale=0,
                    min_width=150,
                )
                download_feedback_btn = gr.Button(
                    "Download feedback",
                    variant="secondary",
                    scale=1,
                )
                download_study_btn = gr.Button(
                    "Download study pack",
                    variant="primary",
                    scale=1,
                )
            download_status = gr.Textbox(
                label="Download status",
                lines=1,
                max_lines=1,
                interactive=False,
                elem_id="download-status",
                show_label=False,
                placeholder="Download status",
            )
            with gr.Row():
                feedback_file = gr.File(label="Feedback file", interactive=False, scale=1)
                study_file = gr.File(
                    label="Study pack (Q&A + concepts)",
                    interactive=False,
                    scale=1,
                )

    return {
        "workspace": workspace,
        "saved_resume": saved_resume,
        "saved_jd": saved_jd,
        "past_conversation": past_conversation,
        "save_resume_btn": save_resume_btn,
        "delete_resume_btn": delete_resume_btn,
        "save_jd_btn": save_jd_btn,
        "delete_jd_btn": delete_jd_btn,
        "load_history_btn": load_history_btn,
        "history_preview": history_preview,
        "history_audio_choice": history_audio_choice,
        "history_audio": history_audio,
        "library_status": library_status,
        "resume_file": resume_file,
        "jd_file": jd_file,
        "auto_save_docs": auto_save_docs,
        "start_button": start_button,
        "reset_button": reset_button,
        "question_output": question_output,
        "question_voice": question_voice,
        "voice_input": voice_input,
        "submit_button": submit_button,
        "transcript_output": transcript_output,
        "status_output": status_output,
        "feedback_button": feedback_button,
        "feedback_output": feedback_output,
        "download_format": download_format,
        "download_feedback_btn": download_feedback_btn,
        "download_study_btn": download_study_btn,
        "download_status": download_status,
        "feedback_file": feedback_file,
        "study_file": study_file,
    }
