import streamlit as st
import os
import re
import json
import html as _html
import pandas as pd
try:
    from file_processor import process_uploaded_file, detect_sections
except ImportError:
    from file_processor import process_uploaded_file
    def detect_sections(full_text):
        """Fallback si file_processor no exporta detect_sections (p. ej. imagen Docker antigua)."""
        if not full_text or not isinstance(full_text, str):
            return {"relato": "", "reflexion": "", "audio_url": None}
        text = full_text.strip()
        url_pattern = re.compile(r'https?://[^\s<>"\']+', re.IGNORECASE)
        matches = url_pattern.findall(text)
        audio_url = None
        for u in reversed(matches):
            if any(x in u.lower() for x in ('drive', 'dropbox', 'onedrive', '1drv', 'sharepoint', 'youtu', 'soundcloud', 'mp3', 'mp4')):
                audio_url = u.rstrip('.,;:)')
                break
        if not audio_url and matches:
            audio_url = matches[-1].rstrip('.,;:)')
        if audio_url:
            idx = text.find(audio_url)
            if idx >= 0:
                return {"relato": text[:idx].strip(), "reflexion": text[idx:].strip(), "audio_url": audio_url}
        return {"relato": text, "reflexion": "", "audio_url": audio_url}

from analysis_engine import (
    count_words,
    check_orthography,
    transcribe_audio,
    transcribe_audio_url,
    analyze_story_vs_transcription,
    detect_ai_indicators,
    validate_highlights,
    build_fragmentos_retro,
)
from evaluator import Evaluator, NIVELES
from feedback_generator import FeedbackGenerator, build_eval_json_for_llm

st.set_page_config(page_title="AI Evaluador - M2 AI2", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
<style>
  :root {
    --bg: #f5f7fb;
    --panel: #f1f4f8;
    --border: #cfd7e3;
    --text: #111827;
    --muted: #4b5563;
    --accent: #e5eaf1;
  }
  .block-container { padding-top: 1.25rem; padding-bottom: 2.5rem; }
  h1, h2, h3 { letter-spacing: 0.2px; }
  .section-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #111827 !important;
    margin: 0.15rem 0 0.45rem 0;
    padding: 0 0 0.15rem 0;
    border-bottom: 1px solid var(--border);
    line-height: 1.2;
  }
  /* En Streamlit, este wrapper se abre/cierra en bloques separados; lo dejamos neutral
     para evitar "barras" gruesas vacías arriba de los títulos. */
  .section-box {
    background: transparent;
    border: 0;
    border-radius: 0;
    padding: 0;
    margin: 0;
  }
  .subtle { color: var(--muted); font-size: 1.1rem; }
  div[data-testid="stMetricValue"] { font-weight: 650; }
  div[data-testid="stMetricLabel"] { color: var(--muted); }
  .stTextArea textarea, .stTextInput input { border-radius: 10px; }
  .stButton button { border-radius: 10px; }
  .ico { width: 14px; height: 14px; vertical-align: -2px; margin-right: 8px; opacity: 1; color: #1f2937 !important; }
  .section-title .ico { width: 16px; height: 16px; color: #1f2937 !important; display: inline-block; opacity: 1; }
  /* Preview iframe (components.html) */
  div[data-testid="stHtml"] iframe { border-radius: 12px; border: 1px solid var(--border); }
  .mono-box {
    border: 1px solid var(--border);
    border-radius: 12px;
    background: rgba(255,255,255,0.03);
    padding: 10px 12px;
    overflow: auto;
    max-height: 220px;
    margin-bottom: 10px;
  }
  .mono-box pre {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
    font-size: 0.86rem;
    line-height: 1.25rem;
    color: var(--text);
  }
  /* st.code blocks: keep syntax colors but wrap long lines */
  div[data-testid="stCode"] pre, div[data-testid="stCode"] code {
    white-space: pre-wrap !important;
    overflow-wrap: anywhere !important;
    word-break: break-word !important;
  }
</style>
""",
    unsafe_allow_html=True,
)

def _svg_icon(kind: str) -> str:
    icons = {
        "doc": '<svg class="ico" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8 3h7l4 4v14a2 2 0 0 1-2 2H8a3 3 0 0 1-3-3V6a3 3 0 0 1 3-3Z" stroke="currentColor" stroke-width="1.6"/><path d="M15 3v5h5" stroke="currentColor" stroke-width="1.6"/></svg>',
        "analyze": '<svg class="ico" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 19V5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><path d="M8 19V9" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><path d="M12 19V12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><path d="M16 19V7" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><path d="M20 19V10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
        "manual": '<svg class="ico" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M7 3h10a2 2 0 0 1 2 2v16l-4-2-4 2-4-2-4 2V5a2 2 0 0 1 2-2Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>',
        "result": '<svg class="ico" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M7 11l3 3 7-7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" stroke="currentColor" stroke-width="1.6"/></svg>',
        "ai": '<svg class="ico" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><path d="M8 8h8v8H8V8Z" stroke="currentColor" stroke-width="1.6"/><path d="M10 11h4M10 13h4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
        "export": '<svg class="ico" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 3v10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M8 9l4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M4 17v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
    }
    return icons.get(kind, "")

if "processed_data" not in st.session_state:
    st.session_state.processed_data = None
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "evaluation" not in st.session_state:
    st.session_state.evaluation = None
if "feedback" not in st.session_state:
    st.session_state.feedback = None
if "manual_eval" not in st.session_state:
    st.session_state.manual_eval = {}
if "section_story" not in st.session_state:
    st.session_state.section_story = None
if "section_refl" not in st.session_state:
    st.session_state.section_refl = None
if "section_audio_url" not in st.session_state:
    st.session_state.section_audio_url = None
if "student_name" not in st.session_state:
    st.session_state.student_name = ""
if "firma_asesor" not in st.session_state:
    st.session_state.firma_asesor = ""

def parse_student_name_from_filename(filename):
    """Extrae Nombre Apellidos desde Apellidos_Nombre_M02S1AI2."""
    if not filename:
        return ""
    base = os.path.splitext(filename)[0]
    parts = [p.strip() for p in re.split(r"[_\-.]", base) if p.strip()]
    parts = [p for p in parts if p.upper() != "M02S1AI2" and "M02" not in p.upper()]
    if len(parts) >= 2:
        return parts[1] + " " + parts[0]
    return parts[0] if parts else ""

# Indicaciones actitudinales (12) para evaluación manual
INDICACIONES_LABELS = [
    "Relato sobre historia de vida",
    "Extensión 1-2 cuartillas",
    "Fuente Arial 12 pt",
    "Título 'El relato de mi historia'",
    "Párrafo con clases de palabras coloreadas",
    "Colores correctos (verbos verde, sustantivos azul, etc.)",
    "Grabación de audio o video",
    "Duración 2-3 minutos",
    "Carga en nube (Drive, OneDrive, Dropbox)",
    "Liga de acceso al final del documento",
    "Párrafo diferencias oral/escrito (5-10 líneas)",
    "Nombre de archivo Apellidos_Nombre_M02S1AI2",
]

with st.sidebar:
    st.title("Configuración")
    api_key = st.text_input("Gemini API Key", type="password", help="Para generar retroalimentación con IA. Si no la configuras, se puede usar Ollama.")
    ollama_url = st.text_input("Ollama URL (opcional)", value=os.environ.get("OLLAMA_URL", "http://host.docker.internal:11434"), help="Ej. http://host.docker.internal:11434 en Docker")
    ollama_model = st.text_input("Modelo Ollama (opcional)", value=os.environ.get("OLLAMA_MODEL", "mistral"), help="Modelo a usar si no hay API Key de Gemini")
    ollama_model = (ollama_model or "").strip().strip("_") or "mistral"
    if "localhost:11434" in (ollama_url or "").lower():
        st.caption("Si la app corre en Docker, usa `http://host.docker.internal:11434`.")
    st.divider()
    st.markdown("**Firma del Asesor**")
    firma_sidebar = st.text_area(
        "Escribe tu firma completa (multilinea)",
        value=st.session_state.get("firma_asesor", ""),
        height=100,
        placeholder="Ejemplo:\nJorge Eduardo Trejo Zacarías\nAsesor Virtual\nM2C1G85-021.",
        key="firma_asesor_sidebar",
        help="Esta firma aparecerá al final de la retroalimentación generada y en el JSON exportado.",
    )
    st.session_state["firma_asesor"] = firma_sidebar
    st.divider()
    st.info("Sube el archivo del estudiante (Word, PDF, PPTX, imagen, video o audio) para comenzar.")

st.title("Evaluador de Actividades (M2 AI2)")
st.caption("Mi Historia de Vida — Prepa en Línea-SEP")

uploaded_file = st.file_uploader(
    "Subir Archivo (Docx, PDF, PPTX, Image, Video, Audio)",
    type=["docx", "pdf", "pptx", "png", "jpg", "jpeg", "mp4", "mp3", "wav"],
)

if uploaded_file:
    if st.button("Procesar Archivo"):
        with st.spinner("Analizando documento..."):
            result = process_uploaded_file(uploaded_file)
            if result:
                text = result[0]
                html = result[1]
                audio_path = result[2]
                highlights = result[3] if len(result) > 3 else []
                meta = result[4] if len(result) > 4 else {"titulo_ok": False, "fuente_ok": True, "audio_url": None}
                st.session_state.processed_data = {
                    "text": text,
                    "html": html,
                    "audio_path": audio_path,
                    "filename": uploaded_file.name,
                    "highlights": highlights,
                    "meta": meta,
                }
                st.session_state.student_name = parse_student_name_from_filename(uploaded_file.name)
                st.session_state.student_name_input = st.session_state.student_name
                st.session_state.section_story = None
                st.session_state.section_refl = None
                st.session_state.section_audio_url = None
                st.session_state.analysis_results = None
                st.session_state.evaluation = None
                st.session_state.feedback = None
                st.success(f"Archivo {uploaded_file.name} cargado correctamente.")

if st.session_state.processed_data:
    data = st.session_state.processed_data
    meta = data.get("meta", {})
    full_text = data["text"] or ""

    # Defaults: relato = TODO el documento para que el conteo coincida con Word; luego el usuario puede recortar si quiere
    default_story = st.session_state.section_story if st.session_state.section_story is not None else full_text
    default_refl = st.session_state.section_refl if st.session_state.section_refl is not None else (full_text[-800:] if len(full_text) > 800 else full_text)
    audio_url_default = st.session_state.section_audio_url if st.session_state.section_audio_url is not None else (meta.get("audio_url") or "")

    # -------- Segmento 1: Vista previa + Segmentación --------
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{_svg_icon("doc")}Documento</div>', unsafe_allow_html=True)
    col_prev, col_seg = st.columns([1.2, 1.0], gap="large")

    with col_prev:
        st.markdown('<div class="subtle">Vista previa</div>', unsafe_allow_html=True)
        preview_html = meta.get("html_with_highlights") or data.get("html")
        if preview_html:
            st.components.v1.html(preview_html, height=680, scrolling=True)
        else:
            st.text_area("Texto extraído", full_text, height=680, key="preview_text")

    with col_seg:
        st.markdown('<div class="subtle">Segmentación</div>', unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            if st.button("Detectar secciones"):
                sec = detect_sections(full_text)
                st.session_state.section_story = sec.get("relato") or full_text
                st.session_state.section_refl = sec.get("reflexion", "")
                st.session_state.section_audio_url = sec.get("audio_url") or ""
                st.session_state["seg_story"] = st.session_state.section_story
                st.session_state["seg_refl"] = st.session_state.section_refl
                st.session_state["audio_url"] = st.session_state.section_audio_url
                st.rerun()
        with b2:
            if st.button("Usar todo como relato"):
                st.session_state.section_story = full_text
                st.session_state.section_refl = ""
                st.session_state["seg_story"] = st.session_state.section_story
                st.session_state["seg_refl"] = st.session_state.section_refl
                st.rerun()

        story_text = st.text_area(
            "Ejercicio 1 — Relato escrito",
            value=default_story,
            height=180,
            key="seg_story",
        )
        st.caption("Ejercicio 2: clases de palabras (se detectan por sombreado/fondo de color en Word, PDF, PPTX o imagen).")
        refl_text = st.text_area(
            "Ejercicio 4 — Párrafo de reflexión (5–10 líneas)",
            value=default_refl,
            height=140,
            key="seg_refl",
        )
        audio_url = st.text_input(
            "Ejercicio 3 — Enlace al audio/video (liga al final)",
            value=audio_url_default,
            key="audio_url",
        )
        if meta.get("audio_url") and not data.get("audio_path"):
            st.caption("Enlace detectado en el documento. Al ejecutar el análisis, se intentará descargar y transcribir. Si el enlace es privado o requiere permisos, puede fallar.")
        if meta.get("titulo_ok") is not None:
            st.caption(f"Título detectado: {'Sí' if meta.get('titulo_ok') else 'No'} · Fuente Arial 12: {'Sí' if meta.get('fuente_ok', True) else 'No'}")

        nombre_detectado = parse_student_name_from_filename(data["filename"])
        if "student_name_input" not in st.session_state:
            st.session_state.student_name_input = st.session_state.get("student_name") or nombre_detectado
        st.text_input("Nombre del alumno", key="student_name_input")

    st.markdown("</div>", unsafe_allow_html=True)

    # -------- Segmento 2: Análisis automático --------
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{_svg_icon("analyze")}Análisis automático</div>', unsafe_allow_html=True)

    if st.button("Ejecutar análisis"):
        _spin_msg = "Procesando métricas..."
        if audio_url and not data.get("audio_path") and any(
            x in (audio_url or "").lower() for x in ("1drv", "onedrive", "sharepoint")
        ):
            _spin_msg = (
                "Descargando audio de OneDrive y transcribiendo (puede tardar varios minutos)..."
            )
        with st.spinner(_spin_msg):
            story_words = count_words(story_text)
            refl_words = count_words(refl_text)
            refl_lines = max(1, refl_words // 12)

            # Filtrar highlights: solo palabras que aparecen en el segmento "relato"
            story_words_set = set(re.findall(r'\b[\wáéíóúÁÉÍÓÚñÑ]+\b', (story_text or "").lower()))
            filtered_highlights = [
                h for h in data["highlights"]
                if (h.get("word") or "").lower() in story_words_set
            ]
            if meta.get("highlight_fallback_reason"):
                st.caption(f"Detección de resaltados: {meta['highlight_fallback_reason']}")
            highlight_results = validate_highlights(filtered_highlights)
            ortho_count, ortho_details = check_orthography(story_text + " " + refl_text)

            trans_text = ""
            trans_duration = 0.0
            trans_error = None
            if data.get("audio_path"):
                trans_text, trans_duration = transcribe_audio(data["audio_path"])
            elif (audio_url or "").strip():
                trans_text, trans_duration, trans_error = transcribe_audio_url(
                    (audio_url or "").strip()
                )

            ai_info = detect_ai_indicators(story_text)
            sim_info = analyze_story_vs_transcription(story_text, trans_text)
            fragmentos = build_fragmentos_retro(story_text, refl_text, trans_text, max_chars=420)

            st.session_state.analysis_results = {
                "story_words": story_words,
                "refl_words": refl_words,
                "refl_lines": refl_lines,
                "ortho_count": ortho_count,
                "ortho_details": ortho_details,
                "audio_duration": trans_duration,
                "transcription": trans_text,
                "transcription_error": trans_error,
                "ai_indicators": ai_info,
                "similarity": sim_info,
                "highlights": highlight_results,
                "fragmentos": fragmentos,
            }

    if st.session_state.analysis_results:
        res = st.session_state.analysis_results
        c_m, c_frag, c_det = st.columns([1.0, 1.15, 1.15], gap="large")
        with c_m:
            st.markdown("**Métricas**")
            df_metrics = pd.DataFrame(
                [
                    {"Métrica": "Relato (palabras)", "Valor": str(res["story_words"]) if res["story_words"] is not None else "0"},
                    {"Métrica": "Reflexión (líneas aprox.)", "Valor": str(res["refl_lines"]) if res["refl_lines"] is not None else "0"},
                    {"Métrica": "Clases de palabras (acierto)", "Valor": f"{res['highlights']['accuracy']}%"},
                    {"Métrica": "Ortografía (errores)", "Valor": str(res["ortho_count"]) if res["ortho_count"] is not None else "N/A"},
                    {"Métrica": "Audio (segundos)", "Valor": str(round(res["audio_duration"], 1))},
                ]
            )
            st.dataframe(df_metrics, hide_index=True, use_container_width=True, height=220)
            if res.get("transcription_error"):
                st.warning(f"No se pudo transcribir el audio por liga: {res['transcription_error']}")
            if res["similarity"].get("is_suspicious"):
                st.warning(f"Similitud alta ({res['similarity'].get('similarity', 0)}%). Posible lectura.")

        with c_frag:
            st.markdown("**Fragmentos**")
            fr = res.get("fragmentos") or {}
            with st.expander("Relato — snippet", expanded=True):
                st.markdown('<div class="mono-box"><pre>' + _html.escape(fr.get("historia_snippet", "") or "") + "</pre></div>", unsafe_allow_html=True)
            with st.expander("Reflexión — snippet", expanded=False):
                st.markdown('<div class="mono-box"><pre>' + _html.escape(fr.get("reflexion_snippet", "") or "") + "</pre></div>", unsafe_allow_html=True)
            with st.expander("Transcripción — snippet", expanded=True):
                st.markdown('<div class="mono-box"><pre>' + _html.escape(fr.get("transcripcion_snippet", "") or "") + "</pre></div>", unsafe_allow_html=True)

        with c_det:
            st.markdown("**Detalles**")
            if res.get("ortho_details"):
                with st.expander("Ortografía — sugerencias"):
                    for d in (res.get("ortho_details") or [])[:20]:
                        st.markdown(f"- **{d.get('message', '')}** → {d.get('suggestion', '')}")
                        if d.get("context"):
                            st.caption(f"...{d['context'][:140]}...")
            if res.get("highlights", {}).get("total", 0) > 0:
                with st.expander("Clases de palabras — detalle"):
                    st.table(res["highlights"]["details"][:30])
            if res.get("similarity", {}).get("identical_fragments"):
                with st.expander("Similitud — fragmentos idénticos"):
                    st.write(res["similarity"]["identical_fragments"])

        st.divider()
        if st.button("Generar evaluación"):
            eval_metrics = {
                "story_word_count": res["story_words"],
                "refl_word_count": res["refl_words"],
                "refl_line_count": res["refl_lines"],
                "highlights_accuracy": res["highlights"]["accuracy"],
                "highlights_total": res["highlights"]["total"],
                "audio_duration": res["audio_duration"],
                "audio_found": data.get("audio_path") is not None or bool(audio_url),
                "liga_ok": bool(audio_url) or data.get("audio_path") is not None,
                "filename_valid": "_" in data["filename"] and "M02" in data["filename"].upper(),
                "titulo_ok": meta.get("titulo_ok", True),
                "fuente_ok": meta.get("fuente_ok", True),
                "ortho_count": res["ortho_count"],
                "ai_indicators": res["ai_indicators"],
                "similarity_suspicious": res["similarity"].get("is_suspicious", False),
            }
            eval_engine = Evaluator()
            final_results = eval_engine.grade_auto(eval_metrics)
            st.session_state.evaluation = final_results
            st.session_state.segmentacion = {"story": story_text, "refl": refl_text, "transcription": res.get("transcription", "")}
            st.session_state.analysis_for_export = res
            st.success("Evaluación generada.")

    st.markdown("</div>", unsafe_allow_html=True)

    # Evaluación manual completa (rúbrica M2 AI2) (colapsable)
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{_svg_icon("manual")}Evaluación manual</div>', unsafe_allow_html=True)
    with st.expander("Abrir evaluación manual", expanded=False):
        st.caption("Completa criterios según docs/03_data_AI2/m2_ai2_rubrica.md. Al aplicar, se puede exportar JSON/TOON.")
        manual = st.session_state.manual_eval
        st.markdown("**12 indicaciones actitudinales**")
        for i, label in enumerate(INDICACIONES_LABELS):
            st.checkbox(label, value=manual.get(f"ind_{i}", False), key=f"man_ind_{i}")

        st.markdown("**Nivel por criterio**")
        m1, m2, m3, m4, m5 = st.columns(5)
        niveles_opts = ["Experto", "Capacitado", "Aceptable", "Aprendiz", "Requiere Apoyo", "No Evaluable"]
        def _idx(nv):
            return niveles_opts.index(nv) if nv in niveles_opts else 2
        with m1:
            nv_cog = st.selectbox("Cognitivo", niveles_opts, index=_idx(manual.get("nv_cog", "Aceptable")), key="man_cog")
        with m2:
            nv_act = st.selectbox("Actitudinal", niveles_opts, index=_idx(manual.get("nv_act", "Aceptable")), key="man_act")
        with m3:
            nv_com = st.selectbox("Comunicativo", niveles_opts, index=_idx(manual.get("nv_com", "Aceptable")), key="man_com")
        with m4:
            nv_pc = st.selectbox("Pensamiento crítico", niveles_opts, index=_idx(manual.get("nv_pc", "Aceptable")), key="man_pc")
        with m5:
            ded_orig = st.number_input("Deducción originalidad (0-100)", 0, 100, manual.get("ded_orig", 0), key="man_ded")

        puntajes = {n: NIVELES.get(n, 0) for n in niveles_opts}
        total_manual = max(0, (puntajes.get(nv_cog, 0) + puntajes.get(nv_act, 0) + puntajes.get(nv_com, 0) + puntajes.get(nv_pc, 0)) // 4 - ded_orig)
        manual_observ = st.text_area("Observaciones", value=manual.get("observaciones", ""), key="man_obs")

        if st.button("Aplicar evaluación manual"):
            indicadores_values = [st.session_state.get(f"man_ind_{i}", False) for i in range(12)]
            cumplidos_manual = sum(1 for x in indicadores_values if x)
            st.session_state.manual_eval = {
                "total_score": total_manual,
                "observaciones": manual_observ,
                "nv_cog": nv_cog, "nv_act": nv_act, "nv_com": nv_com, "nv_pc": nv_pc,
                "ded_orig": ded_orig,
                **{f"ind_{i}": indicadores_values[i] for i in range(12)},
            }
            st.session_state.evaluation = {
                "cognitivo": {"relato": nv_cog, "clases": nv_cog, "audio": nv_cog, "parrafo": nv_cog, "nivel_global": nv_cog, "score": puntajes.get(nv_cog, 0)},
                "actitudinal": {"level": nv_act, "score": puntajes.get(nv_act, 0), "cumplidos": cumplidos_manual, "total": 12, "indicadores": indicadores_values},
                "comunicativo": {"level": nv_com, "score": puntajes.get(nv_com, 0), "errores_ortografia": None},
                "pensamiento_critico": {"level": nv_pc, "score": puntajes.get(nv_pc, 0)},
                "originalidad": {"deduccion": ded_orig, "nivel": "—"},
                "total_score": total_manual,
                "manual": True,
            }
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.evaluation:
    res = st.session_state.evaluation
    student_name = st.session_state.get("student_name_input") or st.session_state.get("student_name") or parse_student_name_from_filename(st.session_state.processed_data.get("filename", "")) or "Estudiante"

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{_svg_icon("result")}Resultados de la evaluación — {student_name}</div>', unsafe_allow_html=True)

    cog = res["cognitivo"]
    act = res["actitudinal"]
    com = res["comunicativo"]
    pc = res["pensamiento_critico"]
    orig = res["originalidad"]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Cognitivo", (cog.get("nivel_global") or cog.get("relato")), f"{cog.get('score', 0)} pts")
    c2.metric("Actitudinal", act["level"], f"{act.get('score', 0)} pts")
    c3.metric("Comunicativo", com["level"], f"{com.get('score', 0)} pts")
    c4.metric("Pensamiento Crítico", pc["level"], f"{pc.get('score', 0)} pts")
    c5.metric("Originalidad", orig.get("nivel", "—"), f"-{orig.get('deduccion', 0)} ded")

    st.markdown(f"**Puntaje total:** {res['total_score']}/100")
    if res.get("total_sin_deduccion") and res.get("originalidad", {}).get("deduccion", 0) > 0:
        st.caption(f"Deducción por originalidad: -{res['originalidad']['deduccion']} (sin deducción: {res['total_sin_deduccion']})")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{_svg_icon("ai")}Retroalimentación con IA</div>', unsafe_allow_html=True)
    if st.button("Generar retroalimentación"):
        with st.spinner("Generando retroalimentación..."):
            gen = FeedbackGenerator(api_key=api_key, csv_path="docs/01_guias/Compilado M02_RED_DSAyDC.csv", ollama_url=ollama_url or None, ollama_model=ollama_model)
            segmentacion = st.session_state.get("segmentacion") or {}
            fragmentos = build_fragmentos_retro(
                segmentacion.get("story") or (st.session_state.processed_data.get("text") or "")[:2000],
                segmentacion.get("refl") or (st.session_state.processed_data.get("text") or "")[-500:],
                segmentacion.get("transcription") or (st.session_state.analysis_results or {}).get("transcription", ""),
            )
            story_snippet = (st.session_state.processed_data.get("text") or "")[:800]
            feedback = gen.generate_feedback(
                res,
                story_snippet,
                fragmentos=fragmentos,
                student_name=student_name,
                curso="M2",
                asesor_nombre="Asesor",
            )
            st.session_state.feedback = feedback
            st.rerun()

if st.session_state.get("feedback"):
    st.markdown(st.session_state.feedback)
    with st.expander("Ver prompt usado (system + user)"):
        gen = FeedbackGenerator(api_key=api_key, csv_path="docs/01_guias/Compilado M02_RED_DSAyDC.csv", ollama_url=ollama_url or None, ollama_model=ollama_model)
        segmentacion = st.session_state.get("segmentacion") or {}
        fragmentos = build_fragmentos_retro(
            segmentacion.get("story") or (st.session_state.processed_data.get("text") or "")[:2000],
            segmentacion.get("refl") or (st.session_state.processed_data.get("text") or "")[-500:],
            segmentacion.get("transcription") or (st.session_state.analysis_results or {}).get("transcription", ""),
        )
        prompt_preview = gen.get_prompt_preview(
            st.session_state.evaluation,
            (st.session_state.processed_data.get("text") or "")[:800],
            fragmentos=fragmentos,
            student_name=st.session_state.get("student_name_input") or st.session_state.get("student_name") or "Estudiante",
            curso="M2",
            asesor_nombre="Asesor",
        )
        st.markdown('<div class="mono-box" style="background:#eef1f5;border-color:#c7ced8;"><pre style="color:#111827;">' + _html.escape(prompt_preview) + "</pre></div>", unsafe_allow_html=True)
        st.caption("Referencia: docs/03_data_AI2/m2_ai2_retroalimentacion.md")
    # (El cierre del contenedor de retro se hace siempre al final del bloque)

if st.session_state.get("evaluation"):
    # Cerrar contenedor de retro (siempre, haya o no feedback)
    st.markdown("</div>", unsafe_allow_html=True)

# -------- Segmento final: Export y visor JSON --------
if st.session_state.get("evaluation") and st.session_state.get("processed_data"):
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{_svg_icon("export")}Export (JSON / TOON) y visor</div>', unsafe_allow_html=True)

    with st.expander("Abrir export y visor", expanded=False):
        val = Evaluator()
        extra = {
            "filename": st.session_state.processed_data.get("filename", ""),
            "student_name": st.session_state.get("student_name_input") or st.session_state.get("student_name") or parse_student_name_from_filename(st.session_state.processed_data.get("filename", "")),
        }
        extra["firma_asesor"] = st.session_state.get("firma_asesor", "")

        ar = st.session_state.get("analysis_for_export") or st.session_state.get("analysis_results") or {}
        seg = st.session_state.get("segmentacion") or {}
        story_for_export = seg.get("story") or (st.session_state.processed_data.get("text") or "")
        refl_for_export = seg.get("refl") or ""
        trans_for_export = seg.get("transcription") or (ar.get("transcription") or "")
        audio_url_for_export = st.session_state.get("audio_url") or ""

        fragmentos_export = build_fragmentos_retro(story_for_export, refl_for_export, trans_for_export, max_chars=1800)
        def _slice_text(t: str, start: int, length: int) -> str:
            if not t:
                return ""
            t = str(t)
            chunk = t[start:start + length]
            return chunk + ("..." if len(t) > start + length else "")
        def _tail_text(t: str, length: int) -> str:
            if not t:
                return ""
            t = str(t)
            chunk = t[-length:]
            return ("..." if len(t) > length else "") + chunk
        story_len = len(story_for_export or "")
        trans_len = len(trans_for_export or "")
        fragmentos_export["historia_inicio"] = _slice_text(story_for_export, 0, 900)
        fragmentos_export["historia_medio"] = _slice_text(story_for_export, max(0, story_len // 2 - 450), 900)
        fragmentos_export["historia_fin"] = _tail_text(story_for_export, 900)
        fragmentos_export["transcripcion_inicio"] = _slice_text(trans_for_export, 0, 900)
        fragmentos_export["transcripcion_medio"] = _slice_text(trans_for_export, max(0, trans_len // 2 - 450), 900)
        fragmentos_export["transcripcion_fin"] = _tail_text(trans_for_export, 900)

        llm_json = build_eval_json_for_llm(
            st.session_state.evaluation,
            fragmentos_export,
            estudiante_nombre=extra.get("student_name") or "Estudiante",
            curso="M2",
            asesor_nombre="Asesor",
        )

        extra["segments"] = {
            "historia": {"text": story_for_export, "word_count": ar.get("story_words") or count_words(story_for_export)},
            "enlace": {"text": audio_url_for_export, "url": audio_url_for_export},
            "parrafo_comparacion": {"text": refl_for_export, "word_count": ar.get("refl_words") or count_words(refl_for_export), "line_count": ar.get("refl_lines") or 0},
            "transcripcion_audio": {"text": trans_for_export, "error": ar.get("transcription_error")},
        }
        extra["audio"] = {
            "audio_url": audio_url_for_export,
            "download_ok": not bool(ar.get("transcription_error")) and bool(trans_for_export or ""),
            "download_error": ar.get("transcription_error"),
        }
        extra["fragmentos_para_personalizar"] = fragmentos_export
        extra["frases_sugeridas_mapeo"] = llm_json.get("frases_sugeridas_mapeo")
        gen_export = FeedbackGenerator(api_key=api_key, csv_path="docs/01_guias/Compilado M02_RED_DSAyDC.csv", ollama_url=ollama_url or None, ollama_model=ollama_model)
        extra["recursos_sugeridos"] = gen_export.get_suggested_materials(st.session_state.evaluation, max_por_area=3, max_total=10) or []

        if ar:
            extra["metrics"] = {
                "story_length": {"words": ar.get("story_words"), "pages_approx": round(((ar.get("story_words") or 0) / 350), 1) if ar.get("story_words") is not None else None, "status": "Correcta" if 350 <= (ar.get("story_words") or 0) <= 1000 else "Fuera de rango"},
                "comparison_length": {"words": ar.get("refl_words"), "lines_approx": ar.get("refl_lines"), "status": "OK" if 5 <= (ar.get("refl_lines") or 0) <= 10 else "Revisar extensión"},
                "highlight_stats": {"total": (ar.get("highlights") or {}).get("total"), "correct": (ar.get("highlights") or {}).get("correct"), "accuracy": (ar.get("highlights") or {}).get("accuracy")},
                "audio_found": bool(trans_for_export) or (ar.get("audio_duration") or 0) > 0,
                "ai_indicadores": {"frases_tipicas_count": (ar.get("ai_indicators") or {}).get("count", 0), "frases_tipicas_lista": (ar.get("ai_indicators") or {}).get("found", []), "resumen": " | ".join((ar.get("ai_indicators") or {}).get("found", [])) if (ar.get("ai_indicators") or {}).get("found") else ""},
                "orthography_errors": ar.get("ortho_count"),
                "orthography_error_reason": None,
            }
            extra["orthography_matches"] = [
                {"message": x.get("message"), "contexto": x.get("context") or x.get("contexto"), "sugerencia": x.get("suggestion") or x.get("sugerencia")} 
                for x in (ar.get("ortho_details") or [])
            ]
            extra["highlights_detail"] = [
                {"word": d.get("word"), "expected": d.get("expected"), "detected": d.get("detected"), "match": d.get("match")} 
                for d in (((ar.get("highlights") or {}).get("details")) or [])
            ]

        json_data = val.export(st.session_state.evaluation, "json", extra=extra)
        # Build a safe filename using the student name
        import unicodedata
        raw_name = (extra.get("student_name") or "estudiante").strip()
        # Normalizar para quitar acentos
        nfkd_form = unicodedata.normalize('NFKD', raw_name)
        only_ascii = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        # Limpiar caracteres no permitidos y espacios
        safe_name = re.sub(r'[^\w\s-]', '', only_ascii).strip()
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        json_filename = f"evaluacion_{safe_name}_M02AI2.json" if safe_name else "evaluacion_m2_ai2.json"
        prompt_preview = gen_export.get_prompt_preview(
            st.session_state.evaluation,
            (st.session_state.processed_data.get("text") or "")[:800],
            fragmentos=fragmentos_export,
            student_name=extra.get("student_name") or "Estudiante",
            curso="M2",
            asesor_nombre="Asesor",
        )
        prompt_user = ""
        marker = "=== USER (con datos de esta evaluación) ==="
        if marker in prompt_preview:
            prompt_user = prompt_preview.split(marker, 1)[1].strip()
        else:
            prompt_user = prompt_preview
        st.download_button("Descargar JSON", json_data, file_name=json_filename, mime="application/json")
        st.markdown("**Visor JSON**")
        st.code(json_data, language="json")
        st.markdown("**Prompt USER (para retroalimentación IA)**")
        st.markdown('<div class="mono-box" style="background:#eef1f5;border-color:#c7ced8;"><pre style="color:#111827; white-space: pre-wrap;">' + _html.escape(prompt_user) + "</pre></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
