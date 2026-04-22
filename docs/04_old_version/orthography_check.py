"""
Conteo de sugerencias ortográficas/gramaticales con LanguageTool (API pública).
Referencia: m2_ai2_metricas_evaluacion.md §3.3 Errores ortográficos y de puntuación.
Si la API no está disponible o falla, se devuelve None (revisión manual recomendada).
"""
import re

# Límite de caracteres para no sobrecargar la API (ej. 50k)
MAX_CHARS = 50000


def count_orthography_errors(text):
    """
    Envía el texto a LanguageTool (api.languagetool.org) y devuelve el número y el detalle de coincidencias.
    text: str (contenido a revisar, p. ej. historia + reflexión).
    Returns: (int | None, str | None, list | None) — (número de errores; motivo de fallo si no se pudo; lista de detalle para el reporte).
    """
    if not text or not isinstance(text, str):
        return None, "Texto vacío o no es string", None
    text_clean = text.strip()
    if len(text_clean) < 20:
        return 0, None, []
    if len(text_clean) > MAX_CHARS:
        text_clean = text_clean[:MAX_CHARS]

    try:
        import urllib.request
        import urllib.parse
        import json

        url = "https://api.languagetool.org/v2/check"
        data = urllib.parse.urlencode({
            "text": text_clean,
            "language": "es",
        }).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded; charset=utf-8")
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        matches = result.get("matches", [])
        # Lista para el reporte: mensaje, contexto, sugerencia
        detalle = []
        for m in matches:
            msg = m.get("message") or m.get("shortMessage") or "Error detectado"
            ctx = (m.get("context") or {}).get("text") or ""
            if len(ctx) > 120:
                ctx = ctx[:118] + "…"
            repl = m.get("replacements") or []
            sug = repl[0].get("value", "").strip() if repl else ""
            if len(sug) > 60:
                sug = sug[:58] + "…"
            detalle.append({"message": msg, "contexto": ctx, "sugerencia": sug})
        return len(matches), None, detalle
    except Exception as e:
        return None, str(e), None
