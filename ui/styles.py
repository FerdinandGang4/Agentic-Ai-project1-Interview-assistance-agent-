"""Professional Gradio CSS for the interview coach UI."""

APP_CSS = """
:root {
    --ink: #1c2b28;
    --muted: #6b7c77;
    --line: #e2ebe7;
    --surface: #ffffff;
    --canvas: #f3f6f4;
    --accent: #0f6b5c;
    --accent-soft: #e7f3ef;
    --brand: #4a2f6b;
    --brand-soft: #efe8f7;
    --danger: #b42318;
    --radius: 12px;
}

body {
    background:
        radial-gradient(1200px 420px at 8% -10%, #e8ddf5 0%, transparent 55%),
        radial-gradient(900px 380px at 100% 0%, #d9efe8 0%, transparent 50%),
        var(--canvas) !important;
}

.gradio-container {
    box-sizing: border-box !important;
    width: 100% !important;
    max-width: 1180px !important;
    margin: 0 auto !important;
    padding: 18px 18px 28px !important;
    color: var(--ink) !important;
    font-family: "Segoe UI", "Aptos", "Trebuchet MS", sans-serif !important;
}

.gradio-container .main.fillable {
    box-sizing: border-box !important;
    max-width: none !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}

/* ----- Header ----- */
#app-header {
    align-items: center !important;
    background: linear-gradient(135deg, #3f275c 0%, #523873 58%, #5d3f82 100%) !important;
    border: none !important;
    border-radius: var(--radius) !important;
    box-shadow: 0 10px 28px rgb(61 38 92 / 18%);
    gap: 12px !important;
    margin-bottom: 14px !important;
    padding: 16px 18px !important;
}

#header-copy {
    margin: 0 !important;
}

/* Force light contrast on purple header (Gradio defaults use dark ink) */
#app-header #header-copy,
#app-header #header-copy p,
#app-header #header-copy strong,
#app-header #header-copy span,
#app-header #header-copy * {
    color: #f0e8fa !important;
}

#app-header #header-copy p {
    color: #f0e8fa !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 1.3px !important;
    margin: 0 0 4px !important;
    opacity: 1 !important;
    text-transform: uppercase !important;
}

#header-copy h1,
#header-copy h1 strong,
#app-header #header-copy h1,
#app-header #header-copy h1 * {
    color: #ffffff !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    line-height: 1.15 !important;
    margin: 0 !important;
}

#user-panel {
    align-items: center !important;
    display: flex !important;
    flex-direction: row !important;
    gap: 10px !important;
    justify-content: flex-end !important;
}

.user-chip {
    align-items: center;
    background: rgb(255 255 255 / 12%);
    border: 1px solid rgb(255 255 255 / 16%);
    border-radius: 999px;
    color: #f3eef9;
    display: flex;
    gap: 8px;
    max-width: 240px;
    padding: 6px 12px 6px 6px;
}

.user-chip-guest,
.user-chip-guest span {
    color: #f0e8fa !important;
    justify-content: center;
    padding: 8px 14px;
}

.user-avatar {
    align-items: center;
    background: linear-gradient(145deg, #1a8f7a, #0f6b5c);
    border-radius: 50%;
    color: #fff;
    display: flex;
    flex-shrink: 0;
    font-size: 12px;
    font-weight: 700;
    height: 28px;
    justify-content: center;
    width: 28px;
}

.user-meta {
    display: flex;
    flex-direction: column;
    gap: 0;
    min-width: 0;
}

.user-meta strong {
    color: #fff;
    font-size: 12px;
    line-height: 1.2;
}

.user-meta span {
    color: #d7c8ea;
    font-size: 10px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

#logout-button {
    background: rgb(255 255 255 / 10%) !important;
    border: 1px solid rgb(255 255 255 / 18%) !important;
    color: #f4eefb !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    min-height: 34px !important;
    min-width: 84px !important;
    padding: 0 12px !important;
    width: auto !important;
}

#logout-button:hover {
    background: rgb(255 255 255 / 18%) !important;
    filter: none !important;
}

/* ----- Cards / panels ----- */
.panel-card {
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: var(--radius) !important;
    box-shadow: 0 1px 2px rgb(28 43 40 / 3%), 0 8px 24px rgb(28 43 40 / 4%);
    margin-bottom: 12px !important;
    padding: 14px 14px 12px !important;
}

#auth-section,
#document-section,
#session-section,
#results-section {
    border-bottom: none !important;
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
}

.section-heading h3 {
    color: var(--muted) !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 0.7px !important;
    margin: 0 0 10px !important;
    text-transform: uppercase !important;
}

.section-eyebrow {
    color: var(--muted);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.7px;
    margin: 0 0 10px;
    text-transform: uppercase;
}

/* ----- Status strip ----- */
#status-output textarea {
    background: var(--accent-soft) !important;
    border: 1px solid #cfe5dd !important;
    color: #1f5f52 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    min-height: 38px !important;
}

#auth-status textarea,
#download-status textarea {
    background: #f7f9f8 !important;
    border: 1px solid var(--line) !important;
    color: var(--muted) !important;
    font-size: 12px !important;
    min-height: 36px !important;
}

/* ----- Question / answer ----- */
#question-output textarea {
    background: linear-gradient(180deg, #f4faf7 0%, #eef7f3 100%) !important;
    border: 1px solid #d5e8e0 !important;
    border-left: 4px solid var(--accent) !important;
    color: var(--ink) !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    line-height: 1.5 !important;
    min-height: 96px !important;
    padding: 12px 14px !important;
}

#transcript-output textarea,
#feedback-output textarea {
    background: #fbfcfc !important;
    border: 1px solid var(--line) !important;
    color: var(--ink) !important;
    font-size: 13px !important;
    line-height: 1.5 !important;
}

#interviewer-column,
#candidate-column {
    background: #fbfcfc;
    border: 1px solid var(--line);
    border-radius: 10px;
    min-width: 0;
    padding: 10px !important;
}

#interview-section {
    gap: 12px !important;
}

/* Shrink bulky Gradio file dropzones a bit */
#document-section .wrap,
#document-section [data-testid="file"] {
    min-height: 0 !important;
}

#document-section button,
#document-section .or {
    font-size: 12px !important;
}

#download-controls {
    align-items: end !important;
    gap: 10px !important;
    margin: 6px 0 4px !important;
}

#library-section {
    padding-bottom: 10px !important;
}

#library-status textarea {
    background: #f7f9f8 !important;
    border: 1px solid var(--line) !important;
    color: var(--muted) !important;
    font-size: 12px !important;
    min-height: 34px !important;
}

.history-preview {
    background: #fbfcfc;
    border: 1px solid var(--line);
    border-radius: 8px;
    color: var(--ink);
    font-size: 12px;
    line-height: 1.45;
    max-height: 180px;
    overflow: auto;
    padding: 10px 12px;
}

.history-preview.muted,
.history-preview .muted {
    color: var(--muted);
}

.history-meta {
    color: var(--muted);
    font-size: 11px;
    margin: 4px 0 8px;
}

.history-turn {
    border-top: 1px solid var(--line);
    margin-top: 8px;
    padding-top: 8px;
}

.history-turn .hq {
    font-weight: 650;
    margin-bottom: 4px;
}

.history-turn .ha {
    color: #3d524c;
}

.history-feedback {
    background: var(--accent-soft);
    border-radius: 8px;
    margin-top: 10px;
    padding: 8px 10px;
}

/* ----- Buttons ----- */
.gradio-container button {
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 650 !important;
    min-height: 36px !important;
    transition: background 120ms ease, border-color 120ms ease, transform 120ms ease !important;
}

.gradio-container button.primary {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: #fff !important;
    box-shadow: 0 6px 14px rgb(15 107 92 / 18%);
}

.gradio-container button.secondary {
    background: var(--accent-soft) !important;
    border-color: #cfe3dc !important;
    color: #1a5f52 !important;
}

.gradio-container button:hover {
    filter: none !important;
    transform: translateY(-1px);
}

#start-interview,
#login-button {
    min-width: 110px;
}

#reset-interview,
#register-button {
    min-width: 110px;
}

/* ----- Inputs ----- */
.gradio-container input,
.gradio-container textarea {
    border-radius: 8px !important;
}

.gradio-container input:focus,
.gradio-container textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgb(15 107 92 / 12%) !important;
}

.gradio-container label,
.gradio-container .label-wrap span {
    color: var(--muted) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}

/* ----- Footer ----- */
#app-footer {
    margin-top: 8px;
}

.app-footer-inner {
    align-items: center;
    background: #2f2144;
    border-radius: 10px;
    color: #ddd3ea;
    display: flex;
    font-size: 11px;
    justify-content: space-between;
    padding: 10px 14px;
}

.app-footer-inner strong {
    color: #fff;
    font-size: 10px;
    letter-spacing: 0.8px;
}

footer:not(.app-footer-inner) {
    display: none !important;
}

@media (max-width: 820px) {
    .gradio-container {
        max-width: 100% !important;
        padding: 12px !important;
    }

    #app-header {
        flex-direction: column !important;
        align-items: stretch !important;
    }

    #user-panel {
        justify-content: space-between !important;
        width: 100%;
    }

    #header-copy h1 {
        font-size: 20px !important;
    }

    #interviewer-column,
    #candidate-column {
        margin-bottom: 8px;
    }
}
"""
