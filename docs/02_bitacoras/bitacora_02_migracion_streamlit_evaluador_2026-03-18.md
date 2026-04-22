---
Title: "Migración de Evaluador n8n a Aplicación Streamlit Standalone"
Filename: "bitacora_02_migracion_streamlit_evaluador_2026-03-18"
Date: 2026-03-18
Author: Jorge A. Trec-Interián
Language_stack: ["Python", "Docker"]
Tools: ["Streamlit", "Tesseract OCR", "Faster-Whisper", "Gemini Pro", "Pandas", "FFmpeg"]
Objectives: "Migrar el flujo de evaluación de n8n a una app standalone para mejorar la flexibilidad y soporte multiformato."
tags: ["streamlit", "evaluacion", "ocr", "transcripcion", "ia", "gemini"]
Description: "Desarrollo de una aplicación Streamlit que permite subir archivos (Word, PDF, PPTX, Imágenes, Video, Audio), segmentar contenido, transcribir medios y generar retroalimentación automática con IA."
---

# Bitácora | Migración de Evaluador n8n a Streamlit
## 2026-03-18 - Desarrollo e Implementación de la App Evaluadora

**Files**: app.py, file_processor.py, analysis_engine.py, evaluator.py, feedback_generator.py, Dockerfile, docker-compose.yml  
**Directories**: D:/CODE/Code3_Coding and Data/20260318_M02S1AI2_app_evaluador/  
**Tags**: #streamlit #evaluacion #ocr #transcripcion #ia #gemini #docker  
**Objective**: Crear una herramienta que reduzca la fricción en la evaluación de la actividad M2 AI2, permitiendo segmentación manual y soporte para múltiples formatos de entrega.  
**Segment**: Data Science / App Development / IA Integration

### Descripción del Proceso

Se realizó la migración completa del sistema de evaluación que anteriormente residía en n8n. Los cambios principales incluyen:

1.  **Flexibilidad en la Entrada**: La app ahora acepta formatos que n8n procesaba con dificultad o que requerían flujos externos complejos, como videos (extrayendo audio) e imágenes (usando OCR).
2.  **Interfaz de Segmentación**: Se implementó una previsualización que permite al asesor identificar manualmente las secciones críticas (Relato, Reflexión, Audio) si los algoritmos automáticos no coinciden con el formato del estudiante.
3.  **Modularización**: La lógica de procesamiento, análisis lingüístico (spaCy), transcripción (Whisper) y evaluación (Rúbrica) se separó en módulos de Python (`file_processor.py`, `analysis_engine.py`, etc.).
4.  **Retroalimentación Personalizada**: Integración con la API de Gemini Pro para generar comentarios empáticos y sugerencias de materiales basadas en un compilado de recursos CSV.
5.  **Contenedorización**: Todo el stack se configuró en un Dockerfile que incluye dependencias del sistema como `tesseract-ocr` y `ffmpeg`.

---

## 📋 Resumen

Migración exitosa del flujo de evaluación a una interfaz visual en Streamlit, optimizada para el manejo de "entregas no estándar" y con integración de IA para retroalimentación.

## 📁 Archivos Involucrados

### Input
- Archivos de estudiantes: `docx`, `pdf`, `pptx`, `mp4`, `mp3`, `jpg`, `png`.
- Materiales de apoyo: `Compilado M02_RED_DSAyDC.csv`.

### Output
- Reportes: `JSON` y `TOON` (Token-Oriented Object Notation).
- Retroalimentación: Texto Markdown generado por LLM.

## 🔄 Proceso

1.  **Extracción**: Conversión de medios a texto/audio reproducible.
2.  **Análisis**: Conteo de palabras, validación de colores gramaticales (POS), detección de indicadores de IA y similitud texto-audio.
3.  **Evaluación**: Aplicación de la rúbrica M2 AI2 (Automática con ajuste manual).
4.  **Generación de FB**: Prompting estructurado a Gemini Pro.

## 🔍 Problemas Identificados

- **Formato de entrega**: Los estudiantes a veces entregan capturas de pantalla o videos de su lectura. 
    - *Solución*: Implementación de OCR y extracción de audio vía MoviePy/FFmpeg.
- **Peso de modelos**: Whisper y spaCy pueden hacer la imagen Docker pesada.
    - *Solución*: Uso de `faster-whisper` y `es_core_news_sm` para balancear rendimiento y peso.

## 📊 Resultados

- Reducción del tiempo de evaluación por tarea.
- Mayor precisión en la identificación de errores de ortografía y gramática.
- Consistencia en la retroalimentación enviada a los estudiantes.

---

**Autor:** Jorge A. Trec-Interián  
**Última actualización:** 2026-03-18  
**Estado:** Completado
