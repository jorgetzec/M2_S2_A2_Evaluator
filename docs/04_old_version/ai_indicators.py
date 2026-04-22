"""
Indicadores genéricos de posible contenido generado por IA (M2 AI2 - Mi Historia de Vida).
Referencia: docs/01_guias/m2_ai2_metricas_evaluacion.md §5 Red flags para IA/plagio.
No sustituye revisión humana; aporta señales para el reporte.
"""
import re


# Frases típicas de redacción IA (español): (patrón, etiqueta para reporte)
FRASES_TIPICAS_IA = [
    (r"\ben conclusión\b", "en conclusión"),
    (r"\bes importante mencionar\b", "es importante mencionar"),
    (r"\ba lo largo de mi vida\b", "a lo largo de mi vida"),
    (r"\ben resumen\b", "en resumen"),
    (r"\bcabe destacar\b", "cabe destacar"),
    (r"\bes fundamental\b", "es fundamental"),
    (r"\bdesde mi perspectiva\b", "desde mi perspectiva"),
    (r"\ben mi experiencia\b", "en mi experiencia"),
    (r"\bcomo se mencionó\b", "como se mencionó"),
    (r"\ben este sentido\b", "en este sentido"),
    (r"\bde esta manera\b", "de esta manera"),
    (r"\ben definitiva\b", "en definitiva"),
    (r"\ben términos generales\b", "en términos generales"),
    (r"\ba nivel personal\b", "a nivel personal"),
    (r"\basí mismo\b", "así mismo"),
    (r"\bpor otro lado\b", "por otro lado"),
    (r"\bde igual manera\b", "de igual manera"),
    (r"\ben consecuencia\b", "en consecuencia"),
    (r"\bno obstante\b", "no obstante"),
    (r"\bes decir\b", "es decir"),
    (r"\bpor consiguiente\b", "por consiguiente"),
    (r"\bcomo resultado\b", "como resultado"),
    (r"\ben primer lugar\b", "en primer lugar"),
    (r"\bfinalmente\b", "finalmente"),
]

# Patrones que sugieren mención explícita de IA/prompt
MENciones_IA = [
    r"\bprompt\b", r"\bcomo modelo\b", r"\binteligencia artificial\b",
    r"\bIA\b", r"\bchatgpt\b", r"\bopenai\b", r"\bgenerado por\b",
]

# Preguntas genéricas al final de párrafos (común en respuestas IA)
PREGUNTAS_FINALES = [
    r"\?\s*$",  # oración que termina en ?
    r"¿qué te parece\??", r"¿qué opinas\??", r"¿qué piensas\??",
    r"¿te gustaría\??", r"¿has considerado\??", r"¿no crees\??",
]


def detect_ai_indicators(text):
    """
    Analiza un texto y devuelve indicadores que pueden sugerir uso de IA.
    text: str (p. ej. historia + párrafo de reflexión concatenados).
    Returns: dict con conteos y resumen para el reporte.
    """
    if not text or not isinstance(text, str):
        return {
            "guion_largo_count": 0,
            "guion_largo_frecuente": False,
            "frases_tipicas_count": 0,
            "frases_tipicas_lista": [],
            "divisores_lineas": False,
            "preguntas_finales_count": 0,
            "menciones_prompt_ia": False,
            "resumen": "Texto insuficiente para analizar.",
        }

    text_clean = text.replace("\r", "\n")
    palabras_aprox = len(text.split())
    if palabras_aprox < 50:
        return {
            "guion_largo_count": 0,
            "guion_largo_frecuente": False,
            "frases_tipicas_count": 0,
            "frases_tipicas_lista": [],
            "divisores_lineas": False,
            "preguntas_finales_count": 0,
            "menciones_prompt_ia": False,
            "resumen": "Texto muy breve; no se calcularon indicadores.",
        }

    # Guion largo / em-dash (— o -- usado como em-dash)
    guion_largo = len(re.findall(r"—|(?<=[\s])--(?=[\s])", text))
    guion_frecuente = guion_largo > max(2, palabras_aprox / 250)  # más de 2 o 1 cada ~250 pal

    # Divisores: líneas de solo guiones, asteriscos o underscores (---, ***, ___)
    lineas = text_clean.split("\n")
    divisores = sum(1 for L in lineas if re.match(r"^[\s\-*_]{3,}$", L.strip()))

    # Frases típicas
    texto_lower = text.lower()
    frases_encontradas = []
    for pat, label in FRASES_TIPICAS_IA:
        if re.search(pat, texto_lower, re.IGNORECASE):
            frases_encontradas.append(label)

    # Menciones explícitas de IA/prompt
    menciones_ia = any(re.search(p, texto_lower, re.IGNORECASE) for p in MENciones_IA)

    # Preguntas al final (por párrafo)
    parrafos = [p.strip() for p in text_clean.split("\n\n") if p.strip()]
    preguntas_fin = 0
    for p in parrafos:
        if re.search(r"\?\s*$", p):
            preguntas_fin += 1
        for pat in PREGUNTAS_FINALES[1:]:
            if re.search(pat, p, re.IGNORECASE):
                preguntas_fin += 1
                break

    # Resumen breve para reporte
    partes = []
    if guion_frecuente:
        partes.append("uso frecuente de guion largo (—)")
    if frases_encontradas:
        partes.append(f"frases típicas de redacción formal/IA ({len(frases_encontradas)}): " + ", ".join(frases_encontradas[:5]))
    if divisores > 0:
        partes.append(f"divisores de bloque con líneas (---/***) ({divisores})")
    if preguntas_fin > 1:
        partes.append(f"preguntas al cierre de párrafos ({preguntas_fin})")
    if menciones_ia:
        partes.append("posible mención de IA/prompt")

    resumen = "; ".join(partes) if partes else "Sin indicadores claros de IA en el texto analizado."

    return {
        "guion_largo_count": guion_largo,
        "guion_largo_frecuente": guion_frecuente,
        "frases_tipicas_count": len(frases_encontradas),
        "frases_tipicas_lista": frases_encontradas[:10],
        "divisores_lineas": divisores > 0,
        "divisores_count": divisores,
        "preguntas_finales_count": preguntas_fin,
        "menciones_prompt_ia": menciones_ia,
        "palabras_analizadas": palabras_aprox,
        "resumen": resumen,
    }
