# App Evaluador M2 AI2 - Walkthrough

The evaluation workflow has been migrated from n8n to a standalone Streamlit application. This provides a more robust and user-friendly experience for grading student assignments.

## Features Implemented

- **Multi-format Support**: Process `.docx`, `.pdf`, `.pptx`, Images (OCR), Video, and Audio.
- **Visual Segmentation**: Preview the document and manually select segments for analysis.
- **Automated Analysis**:
    - POS Tagging and word highlight validation.
    - Word count and extension check.
    - Orthography check via LanguageTool.
    - Transcription of audio/video using Faster-Whisper.
- **Manual Fallback**: If a file is non-standard, use the manual evaluation form to fill the rubric.
- **LLM Feedback**: Personalized, empathetic feedback using Gemini Pro.
- **Compact Export**: Download results in JSON or the new **TOON** (Token-Oriented Object Notation) format.

## How to Run

### Prerequisites
- Docker and Docker Compose installed.
- Gemini API Key (Optional but recommended for feedback).

### Setup and Launch
1.  Open a terminal in `D:\CODE\Code3_Coding and Data\20260318_M02S1AI2_app_evaluador`.
2.  Run the following command:
    ```bash
    docker-compose up --build
    ```
3.  Open your browser at `http://localhost:8501`.

## Usage Guide

1.  **Sidebar**: Enter your Gemini API Key.
2.  **Upload**: Select the student's file.
3.  **Preview**: Check the extracted text or HTML.
4.  **Segment**: Copy/Paste the story and reflection sections into the respective fields if the automatic defaults need adjustment.
5.  **Analyze**: Click "Ejecutar Análisis" to get word counts and transcription.
6.  **Evaluate**: Review the auto-populated rubric levels and adjust them as needed.
7.  **Export**: Download the JSON/TOON files for your records.

---

### Folder Structure
- [app.py](file:///D:/CODE/Code3_Coding%20and%20Data/20260318_M02S1AI2_app_evaluador/app.py): Main UI.
- [file_processor.py](file:///D:/CODE/Code3_Coding%20and%20Data/20260318_M02S1AI2_app_evaluador/file_processor.py): Media extraction logic.
- [analysis_engine.py](file:///D:/CODE/Code3_Coding%20and%20Data/20260318_M02S1AI2_app_evaluador/analysis_engine.py): NLP and Transcription logic.
- [evaluator.py](file:///D:/CODE/Code3_Coding%20and%20Data/20260318_M02S1AI2_app_evaluador/evaluator.py): Rubric and grading.
- [feedback_generator.py](file:///D:/CODE/Code3_Coding%20and%20Data/20260318_M02S1AI2_app_evaluador/feedback_generator.py): Gemini integration.
- [Dockerfile](file:///D:/CODE/Code3_Coding%20and%20Data/20260318_M02S1AI2_app_evaluador/Dockerfile) & [docker-compose.yml](file:///D:/CODE/Code3_Coding%20and%20Data/20260318_M02S1AI2_app_evaluador/docker-compose.yml): Infrastructure.
