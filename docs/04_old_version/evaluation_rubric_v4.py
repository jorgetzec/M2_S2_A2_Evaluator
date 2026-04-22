"""
Métricas de evaluación v4 (flexibles) – M2 AI2 – Mi Historia de Vida.
Basado en evaluation_rubric.py con umbrales más tolerantes.
Referencia: docs/01_guias/m2_ai2_metricas_evaluacion.md

Filosofía v4: permitir un margen de tolerancia en cada métrica
para que errores menores no penalicen excesivamente al estudiante.
"""

NIVELES = {
    "Experto": 100, "Capacitado": 90, "Aceptable": 80,
    "Aprendiz": 70, "Requiere Apoyo": 60, "No Evaluable": 0,
}


# ---------------------------------------------------------------------------
# Funciones auxiliares de nivel
# ---------------------------------------------------------------------------

def _nivel_extension_v4(palabras):
    """Nivel para extensión del relato (1-2 cuartillas).
    Stricter v4: 350-1000 → Experto.
    Penalización más fuerte si sale de este rango.
    """
    if palabras is None or palabras == 0:
        return "Requiere Apoyo"
    if 350 <= palabras <= 1000:
        return "Experto"
    if 300 <= palabras < 350 or 1000 < palabras <= 1100:
        return "Capacitado"
    if 200 <= palabras < 300 or 1100 < palabras <= 1250:
        return "Aceptable"
    if 100 <= palabras < 200:
        return "Aprendiz"
    return "Requiere Apoyo"


def _nivel_clases_v4(pct):
    """Nivel para % de aciertos en clases de palabras.
    Flexible: ≥85% → Experto (era ≥90%).
    """
    if pct is None:
        return "No Evaluable"
    if pct >= 85:
        return "Experto"
    if pct >= 75:
        return "Capacitado"
    if pct >= 65:
        return "Aceptable"
    if pct >= 50:
        return "Aprendiz"
    return "Requiere Apoyo"


def _nivel_audio_v4(liga_ok, duracion_ok, audio_found, duracion_seg=None):
    """Nivel para audio/video.
    Rango Experto: 150-210s (3 min ± 30s).
    """
    if not audio_found:
        return "Requiere Apoyo"
    if liga_ok and duracion_ok:
        return "Experto"
    
    # Si tiene liga pero duración fuera de rango, evaluamos según cercanía
    if liga_ok and duracion_seg is not None:
        if 120 <= duracion_seg <= 240:
            return "Capacitado"
        if 90 <= duracion_seg <= 300:
            return "Aceptable"
        return "Aprendiz"
    
    if liga_ok:
        # Liga presente pero duración desconocida
        return "Capacitado"
    
    return "Aprendiz"


def _nivel_parrafo_v4(existe, lineas, palabras):
    """Nivel para párrafo oral vs escrito.
    Flexible: 3-12 líneas → Experto (era 5-10).
    """
    if not existe:
        return "Requiere Apoyo"
    if 3 <= lineas <= 14 and palabras >= 30:
        return "Experto"
    if lineas > 0 and palabras >= 15:
        return "Capacitado"
    return "Aceptable"


def _nivel_actitudinal_v4(cumplidos):
    """Flexible: 10/12 → Experto (era 12/12)."""
    if cumplidos >= 10:
        return "Experto", 100
    if cumplidos >= 9:
        return "Capacitado", 90
    if cumplidos >= 8:
        return "Aceptable", 80
    if cumplidos >= 7:
        return "Aprendiz", 70
    return "Requiere Apoyo", 60


def _nivel_ortografia_v4(errors):
    """Flexible: 0-2 → Experto (era 0)."""
    if errors is None:
        return None, None
    if errors <= 2:
        return "Experto", 100
    if errors <= 5:
        return "Capacitado", 90
    if errors <= 8:
        return "Aceptable", 80
    if errors <= 12:
        return "Aprendiz", 70
    return "Requiere Apoyo", 60


def _nivel_global_cognitivo_v4(niveles_cog):
    """Nivel cognitivo global flexible pero con peso en relato y audio.
    niveles_cog: [relato, clases, audio, parrafo]
    """
    puntajes = [NIVELES.get(n, 0) for n in niveles_cog]
    if not puntajes:
        return "No Evaluable", 0

    # Peso fuerte al relato (índice 0) y audio (índice 2)
    # Si relato o audio no son al menos Capacitado, no puede ser Experto global.
    nivel_relato = niveles_cog[0]
    nivel_audio = niveles_cog[2]
    
    promedio = sum(puntajes) / len(puntajes)
    num_experto = sum(1 for p in puntajes if p >= 100)
    minimo = min(puntajes)

    # Regla de oro: Relato y Audio deben ser excelentes para Experto Global
    if nivel_relato == "Experto" and nivel_audio == "Experto" and num_experto >= 3 and minimo >= 80:
        return "Experto", 100
        
    if promedio >= 95 and nivel_relato in ["Experto", "Capacitado"] and nivel_audio in ["Experto", "Capacitado"]:
        return "Experto", 100
    
    if promedio >= 87:
        return "Capacitado", 90
    if promedio >= 77:
        return "Aceptable", 80
    if promedio >= 67:
        return "Aprendiz", 70
    return "Requiere Apoyo", 60


# ---------------------------------------------------------------------------
# build_evaluation_v4
# ---------------------------------------------------------------------------

def build_evaluation_v4(results, audio_duration_seconds=None):
    """
    Construye evaluación con métricas flexibles (v4).
    results: dict de processor.py (metrics, segments, filename_valid, etc.).
    audio_duration_seconds: duración del audio en segundos (puede ser None).
    Retorna dict con evaluación completa + placeholders para métricas Ollama.
    """
    metrics = results.get("metrics", {})
    segments = results.get("segments", {})
    story = metrics.get("story_length", {})
    comparison = metrics.get("comparison_length", {})
    highlights = metrics.get("highlight_stats", {})

    words_story = story.get("words", 0)
    words_reflection = comparison.get("words", 0)
    lines_reflection = comparison.get("lines_approx", 0)
    accuracy = highlights.get("accuracy")  # None o 0-100
    audio_found = metrics.get("audio_found", False)
    filename_valid = results.get("filename_valid", False)
    has_historia = bool(segments.get("historia", {}).get("text"))
    titulo_ok = results.get("titulo_presente", False)
    fuente_ok = results.get("fuente_arial_12", False)
    orthography_errors = metrics.get("orthography_errors")
    orthography_error_reason = metrics.get("orthography_error_reason")
    orthography_matches = metrics.get("orthography_matches")
    ai_indicators = metrics.get("ai_indicadores")

    # -----------------------------------------------------------------------
    # 1. Cognitivo
    # -----------------------------------------------------------------------

    # 1.1 Relato escrito (v4 más estricto)
    extension_ok = 350 <= words_story <= 1000
    cuartillas = round(words_story / 350, 1) if words_story > 0 else 0
    relato_cumple = extension_ok and titulo_ok and fuente_ok
    nivel_relato = "Experto" if relato_cumple else _nivel_extension_v4(words_story)
    # Si titulo y fuente están bien pero extensión falla, solo baja por extensión
    if extension_ok and titulo_ok and not fuente_ok:
        nivel_relato = "Capacitado"
    if extension_ok and not titulo_ok and fuente_ok:
        nivel_relato = "Capacitado"

    # 1.2 Clases de palabras (flexible)
    nivel_clases = _nivel_clases_v4(accuracy)

    # 1.3 Audio (v4: 150-210 s / 3 min ± 30s)
    duracion_ok = False
    if audio_duration_seconds is not None:
        duracion_ok = 150 <= audio_duration_seconds <= 210
    liga_ok = bool(segments.get("audio_url"))
    nivel_audio = _nivel_audio_v4(liga_ok, duracion_ok, audio_found, audio_duration_seconds)

    # 1.4 Párrafo oral vs escrito (flexible)
    existe_parrafo = bool(segments.get("parrafo_comparacion", {}).get("text"))
    nivel_parrafo = _nivel_parrafo_v4(existe_parrafo, lines_reflection, words_reflection)

    # Nivel cognitivo global (flexible)
    niveles_cog = [nivel_relato, nivel_clases, nivel_audio, nivel_parrafo]
    nivel_cognitivo, puntaje_cognitivo = _nivel_global_cognitivo_v4(niveles_cog)

    # -----------------------------------------------------------------------
    # 2. Actitudinal (flexible)
    # -----------------------------------------------------------------------
    indicaciones = [
        has_historia,                                          # 1. Relato
        extension_ok,                                          # 2. Extensión
        fuente_ok,                                             # 3. Arial 12
        titulo_ok,                                             # 4. Título
        (highlights.get("total") or 0) > 0,                    # 5. Párrafo colores
        (accuracy or 0) >= 40,                                 # 6. Colores correctos (umbral muy bajo)
        audio_found,                                           # 7. Grabación
        duracion_ok if audio_duration_seconds is not None else audio_found,  # 8. Duración
        audio_found,                                           # 9. Carga en nube
        liga_ok,                                               # 10. Liga
        existe_parrafo and words_reflection >= 20,             # 11. Párrafo diferencias
        filename_valid,                                        # 12. Nombre archivo
    ]
    cumplidos = sum(1 for x in indicaciones if x)
    nivel_act, puntaje_act = _nivel_actitudinal_v4(cumplidos)

    # -----------------------------------------------------------------------
    # 3. Comunicativo (parcial; Ollama completa organización y audio calidad)
    # -----------------------------------------------------------------------
    nivel_comunicativo, puntaje_comunicativo = _nivel_ortografia_v4(orthography_errors)

    # Originalidad
    originalidad_resumen = "Por revisión manual según rúbrica."
    if ai_indicators and isinstance(ai_indicators, dict):
        originalidad_resumen = ai_indicators.get("resumen", originalidad_resumen)

    # -----------------------------------------------------------------------
    # Resumen LLM (condensado para prompts)
    # -----------------------------------------------------------------------
    duracion_str = f"{int(audio_duration_seconds)} s" if audio_duration_seconds is not None else "—"
    nombres_indicaciones = [
        "relato", "extensión (1-2 cuartillas)", "Arial 12", "título", "párrafo colores",
        "colores correctos", "grabación", "duración 3 min (+/- 30s)", "nube",
        "liga", "párrafo 5-10 líneas", "nombre archivo",
    ]
    incumplidas = [nombres_indicaciones[i] for i, c in enumerate(indicaciones) if not c]
    incumple_texto = ", ".join(incumplidas) if incumplidas else "ninguna"

    resumen_llm = [
        f"Relato: {words_story} pal ({cuartillas} cuartillas), título={'sí' if titulo_ok else 'no'}, Arial12={'sí' if fuente_ok else 'no'} | Esperado: 350-1000 pal, título, Arial 12",
        f"Clases palabras: {accuracy}% ({highlights.get('correct', 0)}/{highlights.get('total', 0)}) | Esperado: ≥85% Experto",
        f"Audio: liga={'sí' if liga_ok else 'no'}, duración={duracion_str} | Esperado: liga al final, 150-210 s (3 min ± 30s)",
        f"Párrafo oral/escrito: {words_reflection} pal, ~{lines_reflection} líneas | Esperado: 3-12 líneas",
        f"Indicaciones: {cumplidos}/12. No cumple: {incumple_texto}.",
        f"Comunicativo (ortografía): {orthography_errors if orthography_errors is not None else 'no calculado'} errores | 0-2=Experto, 3-5=Capacitado, 6-8=Aceptable, 9-12=Aprendiz, >12=R.Apoyo",
        f"Originalidad (indicadores IA): {originalidad_resumen}",
    ]

    return {
        "cognitivo": {
            "relato_escrito": {
                "extension_ok": extension_ok,
                "palabras": words_story,
                "cuartillas": cuartillas,
                "rango_esperado": "350-1000 palabras (1-2 cuartillas)",
                "titulo_ok": titulo_ok,
                "fuente_ok": fuente_ok,
                "nivel": nivel_relato,
                "puntaje": NIVELES.get(nivel_relato, 0),
            },
            "clases_palabras": {
                "pct_correctas": accuracy,
                "total": highlights.get("total", 0),
                "correctas": highlights.get("correct", 0),
                "nivel": nivel_clases,
                "puntaje": NIVELES.get(nivel_clases, 0),
            },
            "audio": {
                "presente": audio_found,
                "liga_ok": liga_ok,
                "duracion_segundos": audio_duration_seconds,
                "duracion_ok": duracion_ok,
                "rango_esperado": "150-210 s (3 min ± 30s)",
                "nivel": nivel_audio,
                "puntaje": NIVELES.get(nivel_audio, 0),
            },
            "parrafo_oral_escrito": {
                "existe": existe_parrafo,
                "lineas": lines_reflection,
                "palabras": words_reflection,
                "extension_ok": existe_parrafo and 3 <= lines_reflection <= 14,
                "rango_esperado": "3-14 líneas (flexiblev4; ideal 5-10)",
                "nivel": nivel_parrafo,
                "puntaje": NIVELES.get(nivel_parrafo, 0),
            },
            "nivel_global": nivel_cognitivo,
            "puntaje_global": puntaje_cognitivo,
        },
        "actitudinal": {
            "indicaciones": indicaciones,
            "cumplidos": cumplidos,
            "total": 12,
            "nivel": nivel_act,
            "puntaje": puntaje_act,
        },
        "comunicativo": {
            "errores_ortografia_puntuacion": orthography_errors,
            "ortografia_motivo_fallo": orthography_error_reason,
            "errores_detalle": orthography_matches,
            "nivel_ortografia": nivel_comunicativo,
            "puntaje_ortografia": puntaje_comunicativo,
            "nota": (
                "Revisar con LenguageTool si no se calculó: https://languagetool.org/es/"
                + (f" Motivo: {orthography_error_reason}" if orthography_error_reason else "")
            ) if orthography_errors is None else None,
            # Placeholders para Ollama (se llenan en n8n nodo 11)
            "organizacion": {
                "claridad": None,
                "coherencia": None,
                "precision": None,
                "extracto_claridad": None,
                "extracto_coherencia": None,
                "extracto_precision": None,
            },
            "netiqueta": {"cumple": True, "nivel": "Experto"},
            "audio_calidad": {
                "calidad_tecnica": None,
                "fluidez": None,
                "comprensibilidad": None,
                "lee_o_narra": None,
                "observaciones": None,
            },
        },
        "pensamiento_critico": {
            # Placeholder para Ollama
            "diferencia_oral_escrito": {
                "identifica": None,
                "nivel_identificacion": None,
                "coherencia_analisis": None,
                "extractos": None,
            },
            "clases_palabras": {
                "comprende": (accuracy or 0) >= 65,
                "nivel": "Experto" if (accuracy or 0) >= 85 else (
                    "Capacitado" if (accuracy or 0) >= 65 else (
                        "Aceptable" if (accuracy or 0) >= 50 else "Aprendiz"
                    )
                ),
            },
        },
        "originalidad": {
            "deduccion": 0,
            "indicadores_ia": ai_indicators,
            "nota": originalidad_resumen,
        },
        "resumen": {
            "puntaje_cognitivo": puntaje_cognitivo,
            "nivel_cognitivo": nivel_cognitivo,
            "puntaje_actitudinal": puntaje_act,
            "nivel_actitudinal": nivel_act,
        },
        "resumen_llm": resumen_llm,
    }
