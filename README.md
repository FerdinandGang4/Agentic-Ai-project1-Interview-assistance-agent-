# AI Interview Coach

An AI-assisted mock interview application that uses a candidate's resume and a target job description to create a more relevant interview practice session.

## Presentation Notes

### 1. The Problem

Candidates often practice with generic questions that do not reflect their experience or the role they are applying for. This project uses both documents as context so interview practice can be more relevant to the candidate and job.

### 2. Project Goal

Demonstrate how a multi-agent workflow can analyze candidate and job information, conduct a structured mock interview, retain context across answers, and provide practical final feedback.

### 3. Multi-Agent Design

| Agent | Responsibility |
| --- | --- |
| Resume and Job Analysis Agent | Extracts relevant skills, strengths, matches, and gaps; creates four tailored questions and prepares the interview context. |
| Interviewer Agent | Presents the prepared questions one at a time and advances the interview in order. |
| Evaluation Agent | Reviews the complete set of questions and answers after the final response and produces overall feedback. |
| Interview Manager Agent | Coordinates the agents, tracks interview progress, stores each question with its answer, and handles session reset. |

A shared base agent provides the OpenAI model interface used by the specialized agents.

### 4. Interview Workflow

1. The candidate uploads a resume and a job description.
2. The analysis agent compares the documents and prepares the question set.
3. The interviewer asks four role-tailored questions, one at a time. The fifth asks whether the candidate has questions for the interviewer.
4. The candidate records an answer. The application transcribes it and stores it with the current question before continuing.
5. After the fifth answer, the evaluation agent reviews the full interview and presents overall feedback.
6. The candidate can reset the session and start another interview.

### 5. Suggested Presentation Demo

1. Explain the problem of practicing with questions that are not specific to a candidate or a role.
2. Show the four-agent responsibilities and how the interview manager controls the sequence.
3. Upload a sample resume and job description, then start the interview.
4. Answer a few questions and show how the transcript is saved before the next question appears.
5. Show the candidate-question finale, final evaluation, and reset control.

For a live demo, prepare sample documents in advance and ensure the application has a valid OpenAI API key. Microphone recording requires a browser with microphone access.

### 6. Technologies

- Python for application logic and agent orchestration
- Gradio for the interactive interface
- OpenAI models for document analysis, question generation, speech transcription, text-to-speech, and evaluation
- `pypdf` and `python-docx` for reading supported document formats

## Run Locally

Install the application dependencies:

```powershell
python -m pip install gradio openai python-dotenv pypdf python-docx
```

Create a `.env` file in the project root with your API key:

```text
OPENAI_API_KEY=your-api-key
```

Start the application from the project root:

```powershell
python app.py
```

The interface accepts resume and job-description files in PDF, DOCX, or TXT format. Keep `.env` private and do not commit API keys.

## Current Scope and Limitations

- The first four questions are tailored during document analysis; the fifth is a fixed question inviting the candidate to ask the interviewer something.
- Answers are collected during the interview and evaluated together after question five. Per-answer feedback and adaptive follow-up generation are not part of the current flow, although they are ideas in the original design.
- Interview state is held in application memory and is cleared by Reset. It is not persisted as a long-term candidate record.
