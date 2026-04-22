"""
Evaluador M2 AI2 - Mi Historia de Vida.
Rúbrica completa: cognitivo (relato, clases, audio, párrafo), actitudinal (12 indicaciones),
comunicativo (ortografía/organización), pensamiento crítico, originalidad (deducción).
Referencia: docs/03_data_AI2/m2_ai2_rubrica.md, m2_ai2_metricas_evaluacion.md
"""

import json

NIVELES = {
    "Experto": 100, "Capacitado": 90, "Aceptable": 80,
    "Aprendiz": 70, "Requiere Apoyo": 60, "No Evaluable": 0,
}

# Duración audio: 2-3 min = 120-180 s (rúbrica oficial); margen 90-210 para Capacitado/Aceptable
DURACION_MIN_EXPERTO, DURACION_MAX_EXPERTO = 120, 180
DURACION_MIN_ACEPTABLE, DURACION_MAX_ACEPTABLE = 90, 210


def _nivel_extension_v4(palabras, titulo_ok=True, fuente_ok=True):
    """Relato 1-2 cuartillas (350-1000 palabras). Titulo/fuente bajan a Capacitado si fallan."""
    if palabras is None or palabras == 0:
        return "Requiere Apoyo"
    if 350 <= palabras <= 1000 and titulo_ok and fuente_ok:
        return "Experto"
    if 350 <= palabras <= 1000 and (titulo_ok or fuente_ok):
        return "Capacitado"
    if 300 <= palabras < 350 or 1000 < palabras <= 1100:
        return "Capacitado"
    if 200 <= palabras < 300 or 1100 < palabras <= 1250:
        return "Aceptable"
    if 100 <= palabras < 200:
        return "Aprendiz"
    return "Requiere Apoyo"


def _nivel_clases_v4(pct):
    if pct is None:
        return "No Evaluable"
    if pct >= 90:
        return "Experto"
    if pct >= 80:
        return "Capacitado"
    if pct >= 70:
        return "Aceptable"
    if pct >= 60:
        return "Aprendiz"
    return "Requiere Apoyo"


def _nivel_audio_v4(liga_ok, duracion_ok, audio_found, duracion_seg=None):
    if not audio_found:
        return "Requiere Apoyo"
    if liga_ok and duracion_ok:
        return "Experto"
    if liga_ok and duracion_seg is not None:
        if DURACION_MIN_ACEPTABLE <= duracion_seg <= DURACION_MAX_ACEPTABLE:
            return "Capacitado"
        if 60 <= duracion_seg <= 300:
            return "Aceptable"
        return "Aprendiz"
    if liga_ok:
        return "Capacitado"
    return "Aprendiz"


def _nivel_parrafo_v4(lineas, palabras):
    """Párrafo diferencias oral/escrito: 5-10 líneas (aprox 3-14 líneas flexibles), palabras >= 30 ideal."""
    if palabras is None:
        palabras = 0
    if palabras < 10:
        return "Requiere Apoyo"
    if 3 <= lineas <= 14 and palabras >= 30:
        return "Experto"
    if lineas > 0 and palabras >= 15:
        return "Capacitado"
    return "Aceptable"


def _nivel_actitudinal_v4(cumplidos, total=12):
    """12 indicaciones: 100%=Experto, 90%=Capacitado, etc."""
    if cumplidos >= total:
        return "Experto", 100
    if cumplidos >= int(total * 0.9):
        return "Capacitado", 90
    if cumplidos >= int(total * 0.8):
        return "Aceptable", 80
    if cumplidos >= int(total * 0.7):
        return "Aprendiz", 70
    return "Requiere Apoyo", 60


def _nivel_ortografia_v4(errors):
    """Comunicativo por errores ortografía/sintaxis/puntuación."""
    if errors is None:
        return "Experto", 100  # No calculado: no penalizar
    if errors <= 0:
        return "Experto", 100
    if errors <= 3:
        return "Capacitado", 90
    if errors <= 5:
        return "Aceptable", 80
    if errors <= 8:
        return "Aprendiz", 70
    return "Requiere Apoyo", 60


def _nivel_global_cognitivo_v4(niveles_cog):
    """Nivel cognitivo global: peso a relato y audio."""
    puntajes = [NIVELES.get(n, 0) for n in niveles_cog]
    if not puntajes:
        return "No Evaluable", 0
    nivel_relato, nivel_audio = niveles_cog[0], niveles_cog[2]
    promedio = sum(puntajes) / len(puntajes)
    num_experto = sum(1 for p in puntajes if p >= 100)
    minimo = min(puntajes)
    if nivel_relato == "Experto" and nivel_audio == "Experto" and num_experto >= 3 and minimo >= 80:
        return "Experto", 100
    if promedio >= 87:
        return "Capacitado", 90
    if promedio >= 77:
        return "Aceptable", 80
    if promedio >= 67:
        return "Aprendiz", 70
    return "Requiere Apoyo", 60


def _deduccion_originalidad(ai_indicators, similarity_suspicious):
    """
    Deducción por originalidad (rúbrica): Bien -25, Regular -50, Suficiente -75, Insuficiente -100.
    Solo se aplica por indicios de texto no original/plagio externo (p. ej. frases típicas de IA).
    La similitud alta entre relato y transcripción se registra, pero no penaliza.
    """
    # Política actual: solo penalizar con evidencia explícita de plagio externo.
    # La similitud relato-transcripción y frases genéricas no aplican deducción.
    if (ai_indicators or {}).get("plagio_externo") is True:
        sev = int((ai_indicators or {}).get("plagio_externo_severidad", 25) or 25)
        sev = max(0, min(100, sev))
        if sev <= 25:
            return 25, "Bien"
        if sev <= 50:
            return 50, "Regular"
        if sev <= 75:
            return 75, "Suficiente"
        return 100, "Insuficiente"
    return 0, "Excelente"


class Evaluator:
    def grade_auto(self, metrics):
        """
        Evaluación completa v4.
        metrics debe incluir: story_word_count, refl_word_count, refl_line_count,
        highlights_accuracy, highlights_total, audio_duration, audio_found, liga_ok,
        titulo_ok, fuente_ok, filename_valid, ortho_count (errores ortografía),
        ai_indicators (dict con count/found), similarity_suspicious (bool).
        """
        words_story = metrics.get("story_word_count", 0) or 0
        words_refl = metrics.get("refl_word_count", 0) or 0
        lines_refl = metrics.get("refl_line_count", 0) or 0
        accuracy = metrics.get("highlights_accuracy")
        if accuracy is not None:
            accuracy = float(accuracy)
        highlights_total = metrics.get("highlights_total", 0) or 0
        audio_dur = metrics.get("audio_duration", 0) or 0
        audio_found = metrics.get("audio_found", False)
        liga_ok = metrics.get("liga_ok", False)
        titulo_ok = metrics.get("titulo_ok", True)
        fuente_ok = metrics.get("fuente_ok", True)
        filename_valid = metrics.get("filename_valid", False)
        ortho_count = metrics.get("ortho_count")
        ai_indicators = metrics.get("ai_indicators") or {}
        similarity_suspicious = metrics.get("similarity_suspicious", False)

        # Duración 2-3 min
        duracion_ok = DURACION_MIN_EXPERTO <= audio_dur <= DURACION_MAX_EXPERTO

        # 1. Cognitivo
        nv_relato = _nivel_extension_v4(words_story, titulo_ok, fuente_ok)
        nv_clases = _nivel_clases_v4(accuracy)
        nv_audio = _nivel_audio_v4(liga_ok, duracion_ok, audio_found, audio_dur)
        nv_parrafo = _nivel_parrafo_v4(lines_refl, words_refl)

        niveles_cog = [nv_relato, nv_clases, nv_audio, nv_parrafo]
        nv_cognitivo_global, pt_cognitivo = _nivel_global_cognitivo_v4(niveles_cog)

        # 2. Actitudinal (12 indicaciones)
        indicadores = {
            "relato_minimo_50_palabras": words_story > 50,
            "relato_entre_350_y_1000_palabras": 350 <= words_story <= 1000,
            "fuente_arial_12": fuente_ok,
            "titulo_correcto": titulo_ok,
            "clases_palabras_resaltadas": highlights_total > 0,
            "precision_clases_mayor_60": (accuracy or 0) >= 60,
            "audio_incluido": audio_found,
            "audio_duracion_2_3_min": duracion_ok if audio_dur else False,
            "enlace_audio_funcional": liga_ok,
            "enlace_audio_al_final": liga_ok,
            "parrafo_reflexion_min_5_lineas": lines_refl >= 3 and words_refl >= 15,
            "nombre_archivo_correcto": filename_valid,
        }
        cumplidos = sum(1 for v in indicadores.values() if v)
        nv_act, pt_act = _nivel_actitudinal_v4(cumplidos)

        # 3. Comunicativo (ortografía)
        nv_com, pt_com = _nivel_ortografia_v4(ortho_count)

        # 4. Pensamiento crítico (simplificado: por clases y párrafo)
        if (accuracy or 0) >= 85 and nv_parrafo in ("Experto", "Capacitado"):
            nv_pc, pt_pc = "Experto", 100
        elif (accuracy or 0) >= 65 and nv_parrafo != "Requiere Apoyo":
            nv_pc, pt_pc = "Capacitado", 90
        elif (accuracy or 0) >= 50:
            nv_pc, pt_pc = "Aceptable", 80
        else:
            nv_pc, pt_pc = "Aprendiz", 70

        # 5. Originalidad (deducción)
        deduccion, nivel_orig = _deduccion_originalidad(ai_indicators, similarity_suspicious)

        # Puntaje total: promedio de los 4 criterios menos deducción
        total_sin_deduccion = (pt_cognitivo + pt_act + pt_com + pt_pc) / 4
        total_score = max(0, round(total_sin_deduccion - deduccion))

        results = {
            "cognitivo": {
                "relato": nv_relato,
                "clases": nv_clases,
                "audio": nv_audio,
                "parrafo": nv_parrafo,
                "nivel_global": nv_cognitivo_global,
                "score": pt_cognitivo,
            },
            "actitudinal": {
                "level": nv_act,
                "score": pt_act,
                "cumplidos": cumplidos,
                "total": 12,
                "indicadores": indicadores,
            },
            "comunicativo": {"level": nv_com, "score": pt_com, "errores_ortografia": ortho_count},
            "pensamiento_critico": {"level": nv_pc, "score": pt_pc},
            "originalidad": {"deduccion": deduccion, "nivel": nivel_orig},
            "similitud_relato_audio_alta": bool(similarity_suspicious),
            "total_score": total_score,
            "total_sin_deduccion": round(total_sin_deduccion, 1),
            # Para retroalimentación
            "highlights_accuracy": accuracy,
            "audio_found": audio_found,
            "liga_ok": liga_ok,
            "audio_duration": audio_dur,
            "titulo_ok": titulo_ok,
            "fuente_ok": fuente_ok,
        }
        return results

    def export(self, results, format="json", extra=None):
        """
        Exporta evaluación en JSON o TOON.
        extra: dict opcional con filename, student_name, metrics, orthography_matches,
               highlights_detail, suggestions para incluir en el JSON (estilo versión antigua).
        """
        extra = extra or {}
        if format == "json":
            out = dict(results)
            if extra:
                out["filename"] = extra.get("filename", "")
                out["student_name"] = extra.get("student_name", "")
                if extra.get("metrics"):
                    out["metrics"] = extra["metrics"]
                if extra.get("segments") is not None:
                    out["segments"] = extra["segments"]
                if extra.get("audio") is not None:
                    out["audio"] = extra["audio"]
                if extra.get("fragmentos_para_personalizar") is not None:
                    out["fragmentos_para_personalizar"] = extra["fragmentos_para_personalizar"]
                if extra.get("frases_sugeridas_mapeo") is not None:
                    out["frases_sugeridas_mapeo"] = extra["frases_sugeridas_mapeo"]
                if extra.get("recursos_sugeridos") is not None:
                    out["recursos_sugeridos"] = extra["recursos_sugeridos"]
                if extra.get("orthography_matches") is not None:
                    out["orthography_matches"] = extra["orthography_matches"]
                if extra.get("highlights_detail") is not None:
                    out["highlights_detail"] = extra["highlights_detail"]
                if extra.get("firma_asesor") is not None:
                    out["firma_asesor"] = extra["firma_asesor"]
            return json.dumps(out, indent=2, ensure_ascii=False)
        if format == "toon":
            parts = [
                f"s:{results['total_score']}",
                f"cog:{results['cognitivo'].get('nivel_global', results['cognitivo'].get('relato'))}",
                f"act:{results['actitudinal']['level']}",
                f"com:{results['comunicativo']['level']}",
                f"pc:{results['pensamiento_critico']['level']}",
                f"orig:{results['originalidad']['nivel']}",
                f"ded:{results['originalidad']['deduccion']}",
            ]
            if extra.get("student_name"):
                parts.append(f"nombre:{extra['student_name']}")
            if extra.get("recursos_sugeridos"):
                # Compacto: area=nombre@url;...
                try:
                    rec_parts = []
                    for r in (extra.get("recursos_sugeridos") or [])[:12]:
                        area = (r.get("area") or "general").replace("|", " ").replace(":", " ")
                        nombre = (r.get("nombre") or "").replace("|", " ").replace(":", " ")
                        url = (r.get("url") or "").replace("|", " ").replace(":", " ")
                        if nombre and url:
                            rec_parts.append(f"{area}={nombre}@{url}")
                    if rec_parts:
                        parts.append("recursos:" + ";".join(rec_parts))
                except Exception:
                    pass
            return "|".join(parts)
        return ""
