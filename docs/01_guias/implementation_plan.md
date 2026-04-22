# Streamlit Evaluator App - Implementation Plan

Migrate the existing n8n-based student assignment evaluation workflow to a standalone Streamlit application. This app will provide a user-friendly interface for uploading, segmenting, analyzing, and grading assignments (Word, PDF, PPTX).

## Proposed Changes

### [Core Modules]

#### [NEW] `file_processor.py`(file:///D:/CODE/Code3_Coding%20and%20Data/20260318_M02S1AI2_app_evaluador/file_processor.py)
- Logic to handle Word, PDF, PPTX, Images (OCR), and Video/Audio uploads.
- Convert all to a common HTML/Text format for preview and analysis.
- Use `python-docx`, `pypdf`, `python-pptx`, `pytesseract` (OCR), and `moviepy` (audio extraction).
- Reuse highlighting and POS tagging logic from the original [processor.py](file:///d:/CODE/Code3_Coding%20and%20Data/20260209_n8n_docker_flujos/workflow_scripts/processor.py).

#### [NEW] `analysis_engine.py`(file:///D:/CODE/Code3_Coding%20and%20Data/20260318_M02S1AI2_app_evaluador/analysis_engine.py)
- Modular logic for:
    - Word count and story extension.
    - Highlight identification and validation.
    - Audio transcription (using `faster-whisper`).
    - Orthography check (using LanguageTool API).
    - AI indicator detection.
    - Plagiarism/Repetition check (comparing story vs transcription).

#### [NEW] `evaluator.py`(file:///D:/CODE/Code3_Coding%20and%20Data/20260318_M02S1AI2_app_evaluador/evaluator.py)
- Implement ruby-based grading logic (M2 AI2).
- **Manual Mode**: Provide a structured form to evaluate criteria manually if automation fails.
- Generate JSON/TOON output.

#### [NEW] `feedback_generator.py`(file:///D:/CODE/Code3_Coding%20and%20Data/20260318_M02S1AI2_app_evaluador/feedback_generator.py)
- Integrate with Gemini API for personalized feedback.
- Use the provided CSV `Compilado M02_RED_DSAyDC.csv` to suggest improvement materials.

### [UI Layer]

#### [NEW] `app.py`(file:///D:/CODE/Code3_Coding%20and%20Data/20260318_M02S1AI2_app_evaluador/app.py)
- Main Streamlit interface.
- Sidebar for configuration (API keys, settings).
- Multi-step process: Upload -> Preview/Extract -> Segment -> Analyze -> Evaluate (Auto/Manual) -> Export.

### [Infrastructure]

#### [NEW] `Dockerfile`(file:///D:/CODE/Code3_Coding%20and%20Data/20260318_M02S1AI2_app_evaluador/Dockerfile)
- Include `tesseract-ocr`, `ffmpeg`, and Python dependencies.
#### [NEW] `docker-compose.yml`(file:///D:/CODE/Code3_Coding%20and%20Data/20260318_M02S1AI2_app_evaluador/docker-compose.yml)
#### [NEW] `requirements.txt`(file:///D:/CODE/Code3_Coding%20and%20Data/20260318_M02S1AI2_app_evaluador/requirements.txt)

## Verification Plan

### Automated Tests
- Run `pytest` on core analysis modules with mock data.
- Validate JSON/TOON schema consistency.

### Manual Verification
1.  **Upload Test**: Upload a Word file with highlighted text and verify if categories are correctly identified.
2.  **Segmentation Test**: Use the UI to mark "Story" and "Reflection" sections and verify if word counts update correctly.
3.  **Export Test**: Download the result as JSON and TOON and verify the contents.
4.  **Docker Test**: Run `docker-compose up` and access the app via browser.
