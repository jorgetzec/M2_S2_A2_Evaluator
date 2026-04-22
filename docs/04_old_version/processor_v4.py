"""
Processor v4 – Procesador mejorado para el flujo v4.
Envuelve processor.py y añade:
  - Evaluación con métricas flexibles (evaluation_rubric_v4.py)
  - Datos preparados para los prompts de Ollama (fragmentos de texto)
  - Duración de audio accesible directamente

Uso: python3 processor_v4.py "ruta/archivo.docx"
Salida: JSON en stdout con toda la información necesaria para el flujo v4.
"""

import sys
import json
import os
import tempfile
from pdf2docx import Converter

# Asegurar que el directorio del script está en el path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from processor import process_docx
from evaluation_rubric_v4 import build_evaluation_v4


def _truncate_text(text, max_chars=2000):
    """Trunca texto a max_chars caracteres para optimizar prompts de Ollama."""
    if not text or not isinstance(text, str):
        return ""
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def process_docx_v4(file_path):
    """
    Procesador v4: ejecuta el procesador base (v3) y lo enriquece.
    Retorna dict con toda la información para el flujo v4.
    """
    # 1. Obtener resultados base del procesador existente
    base_results = process_docx(file_path)

    # Si hubo error en la extracción base, retornar directamente
    if base_results.get("errors") and not base_results.get("segments", {}).get("historia", {}).get("text"):
        base_results["version"] = "v4"
        return base_results

    # 2. Extraer duración del audio de la evaluación base (si existe)
    audio_duration = None
    eval_base = base_results.get("evaluation")
    if eval_base and isinstance(eval_base, dict) and not eval_base.get("error"):
        audio_duration = (
            eval_base.get("cognitivo", {})
            .get("audio", {})
            .get("duracion_segundos")
        )

    # 3. Reemplazar evaluación con la versión flexible v4
    base_results["evaluation"] = build_evaluation_v4(
        base_results,
        audio_duration_seconds=audio_duration,
    )

    # 4. Guardar duración como campo de nivel superior para fácil acceso
    base_results["audio_duration_seconds"] = audio_duration

    # 5. Preparar fragmentos de texto para los prompts de Ollama
    segments = base_results.get("segments", {})

    historia_text = segments.get("historia", {}).get("text", "")
    transcripcion_text = segments.get("transcripcion_audio", {}).get("text", "")
    parrafo_text = segments.get("parrafo_comparacion", {}).get("text", "")

    base_results["ollama_inputs"] = {
        "historia_snippet": _truncate_text(historia_text, 2000),
        "transcripcion_snippet": _truncate_text(transcripcion_text, 2000),
        "parrafo_snippet": _truncate_text(parrafo_text, 1000),
        "tiene_historia": len(historia_text.strip()) > 50,
        "tiene_transcripcion": len(transcripcion_text.strip()) > 30,
        "tiene_parrafo": len(parrafo_text.strip()) > 15,
    }

    # 6. Preparar datos resumidos para el reporte (evitar que n8n maneje JSONs enormes)
    highlights = segments.get("highlights", [])
    base_results["highlights_tabla"] = [
        {
            "word": h.get("word", ""),
            "category": h.get("category", ""),
            "pos_detected": h.get("pos_detected", ""),
            "match": h.get("match", False),
        }
        for h in highlights[:40]  # Máximo 40 para el reporte
    ]
    base_results["highlights_total"] = len(highlights)

    # 7. Marcar versión y nombre original
    base_results["version"] = "v4"
    if "original_filename" not in base_results:
        base_results["original_filename"] = base_results.get("filename")

    return base_results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No file path provided", "version": "v4"}))
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(json.dumps({"error": f"File not found: {file_path}", "version": "v4"}))
        sys.exit(1)

    temp_docx = None
    try:
        # Soporte para PDF: convertir a DOCX temporalmente
        if file_path.lower().endswith(".pdf"):
            temp_dir = tempfile.gettempdir()
            filename_base = os.path.basename(file_path).rsplit(".", 1)[0]
            temp_docx = os.path.join(temp_dir, f"{filename_base}_temp.docx")
            
            # Realizar la conversión
            cv = Converter(file_path)
            cv.convert(temp_docx, start=0, end=None)
            cv.close()
            
            processing_path = temp_docx
        else:
            processing_path = file_path

        output = process_docx_v4(processing_path)

        # Si era PDF, restaurar el nombre original en el JSON para el reporte
        if file_path.lower().endswith(".pdf"):
            output["filename"] = os.path.basename(file_path)

        print(json.dumps(output, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e), "version": "v4"}))
    finally:
        # Limpieza de archivo temporal
        if temp_docx and os.path.exists(temp_docx):
            try:
                os.remove(temp_docx)
            except:
                pass
