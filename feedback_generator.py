"""
Generador de retroalimentación M2 AI2.
Sigue la estructura y mapeo de docs/03_data_AI2/m2_ai2_retroalimentacion.md.
Usa Compilado M02_RED_DSAyDC.csv para sugerir recursos por área de mejora.
Soporta: Google GenAI (nuevo SDK), google.generativeai (legacy), u Ollama como fallback.
"""

import os
import json
import urllib.request
import urllib.error
from urllib.parse import urlparse
import pandas as pd

# Preferir nuevo SDK (google.genai); si no está, usar el legacy (google.generativeai)
_USE_NEW_GENAI = False
_genai_client = None
_genai_legacy = None

try:
    from google import genai as _genai_new
    _USE_NEW_GENAI = True
except ImportError:
    try:
        import google.generativeai as _genai_legacy
    except ImportError:
        _genai_legacy = None


def _call_ollama(system_prompt, user_prompt, url=None, model="mistral", timeout=180):
    """
    Llama a Ollama /api/chat (estilo docs/04_old_version/ollama_call_v4.py).
    Devuelve el texto de la respuesta o None si falla.
    """
    base = (url or os.environ.get("OLLAMA_URL") or "http://localhost:11434").rstrip("/")
    if not base.startswith("http"):
        base = "http://" + base

    # Si corre en Docker, localhost suele apuntar al contenedor. Probamos alternativas comunes.
    candidates = [base]
    try:
        p = urlparse(base)
        host = (p.hostname or "").lower()
        if host in ("localhost", "127.0.0.1"):
            netloc_host = p.netloc.split("@")[-1].split(":")[0]
            port = p.port or 11434
            candidates.append(base.replace(netloc_host, "host.docker.internal"))
            candidates.append(f"{p.scheme}://ollama:{port}")
    except Exception:
        pass
    model_name = (model or "").strip().strip("_") or "mistral"
    if ":" not in model_name:
        model_name = f"{model_name}:latest"
    body = json.dumps({
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }).encode("utf-8")
    for b in candidates:
        api_url = b.rstrip("/") + "/api/chat"
        try:
            req = urllib.request.Request(
                api_url,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            out = (data.get("message") or {}).get("content", "").strip()
            if out:
                return out
        except Exception:
            continue
    return None

# Áreas de mejora → palabras clave para filtrar recursos del CSV (Compilado M02_RED_DSAyDC)
AREAS_RECURSOS = {
    "clases_palabras": ["clases de palabras", "categorías gramaticales", "categoria gramatical", "gramática", "verbos", "sustantivos", "adjetivos", "clasificacion"],
    "ortografia": ["ortografía", "acentuación", "puntuación", "corrector", "reglas ortográficas", "signos de puntuación"],
    "comunicacion_oral_escrita": ["comunicación oral", "oral y escrita", "oralidad", "oralidadYescritura", "lifeder", "diferencias"],
    "redaccion": ["redacción", "relato", "narración", "secuencia del relato", "pasos para elaborar"],
    "netiqueta": ["netiqueta", "entornos virtuales"],
}


def _cargar_compilado(csv_path):
    """Carga el CSV de recursos M02. Tolera encoding y nombres de columnas variables."""
    if not csv_path or not os.path.exists(csv_path):
        return None
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            df = pd.read_csv(csv_path, encoding=enc)
            if len(df.columns) >= 9 and len(df) > 0:
                return df
        except Exception:
            continue
    return None


def _columnas_csv(df):
    """Obtiene índices/nombres de columnas del Compilado (Nombre recurso, Palabras clave, Enlace RED)."""
    # CSV: Identificador, Módulo, Categoría, ..., Tema, Nombre del recurso, Palabras clave, Enlace de RED, ...
    n = len(df.columns)
    col_nombre = df.columns[7] if n > 7 else df.columns[1]
    col_claves = df.columns[8] if n > 8 else None
    col_url = df.columns[9] if n > 9 else df.columns[-1]
    for c in df.columns:
        c_low = str(c).lower()
        if "enlace" in c_low or "red" in c_low:
            col_url = c
        if "nombre" in c_low and "recurso" in c_low:
            col_nombre = c
        if "palabra" in c_low and "clave" in c_low:
            col_claves = c
    return col_nombre, col_claves, col_url


def _sugerir_recursos_por_area(df, areas_necesitan_mejora, max_por_area=3, max_total=10):
    """
    Recomienda varios recursos del CSV según las áreas que el alumno debe reforzar.
    areas_necesitan_mejora: lista de claves (ej. ["clases_palabras", "ortografia"]).
    Retorna lista de { nombre, url, area } para que el LLM pueda sugerir varios por necesidad.
    """
    if df is None or not areas_necesitan_mejora:
        return []
    col_nombre, col_claves, col_url = _columnas_csv(df)
    sugeridos = []
    seen_urls = set()

    for area in areas_necesitan_mejora:
        keywords = AREAS_RECURSOS.get(area, [])
        count_area = 0
        if col_claves is not None and keywords:
            texto_claves = df[col_claves].astype(str).str.lower()
            for kw in keywords:
                if count_area >= max_por_area:
                    break
                try:
                    mask = texto_claves.str.contains(kw, na=False, regex=False)
                except Exception:
                    mask = texto_claves.str.contains(kw, na=False)
                for _, row in df[mask].iterrows():
                    if count_area >= max_por_area or len(sugeridos) >= max_total:
                        break
                    url = row.get(col_url)
                    nombre = row.get(col_nombre, "Recurso")
                    if pd.isna(url) or not str(url).strip() or str(url).strip() in seen_urls:
                        continue
                    seen_urls.add(str(url).strip())
                    sugeridos.append({
                        "nombre": str(nombre)[:100],
                        "url": str(url).strip(),
                        "area": area,
                    })
                    count_area += 1
        if count_area == 0:
            # Fallback: filtrar por M02
            col_mod = None
            for c in df.columns:
                if "dulo" in str(c) or "modulo" in str(c).lower():
                    col_mod = c
                    break
            if col_mod is not None:
                try:
                    sub = df[df[col_mod].astype(str).str.contains("M02", na=False)]
                except Exception:
                    sub = df
            else:
                sub = df
            for _, row in sub.head(max_por_area * 2).iterrows():
                if len(sugeridos) >= max_total:
                    break
                url = row.get(col_url)
                nombre = row.get(col_nombre, "Recurso")
                if pd.notna(url) and url and str(url).strip() not in seen_urls:
                    seen_urls.add(str(url).strip())
                    sugeridos.append({"nombre": str(nombre)[:100], "url": str(url).strip(), "area": area})

    return sugeridos[:max_total]


def _mapeo_frases(evaluation_results):
    """Genera frases sugeridas según mapeo métricas → frases del doc de retroalimentación."""
    cog = evaluation_results.get("cognitivo", {})
    act = evaluation_results.get("actitudinal", {})
    com = evaluation_results.get("comunicativo", {})
    pc = evaluation_results.get("pensamiento_critico", {})
    orig = evaluation_results.get("originalidad", {})

    lineas = []
    titulo_ok = evaluation_results.get("titulo_ok", True)
    fuente_ok = evaluation_results.get("fuente_ok", True)
    # Relato
    nv_relato = cog.get("relato", "")
    if nv_relato == "Experto":
        lineas.append("Tu relato se ha apegado al formato y la extensión solicitados.")
    elif nv_relato in ("Capacitado", "Aceptable"):
        pendientes = []
        if not fuente_ok:
            pendientes.append("usar fuente Arial de 12 puntos")
        if not titulo_ok:
            pendientes.append(
                "incluir un título que identifique tu relato (por ejemplo, sobre tu historia personal)"
            )
        if pendientes:
            lineas.append("Recuerda " + " y ".join(pendientes) + ".")
    else:
        lineas.append("Te sugiero ampliar el relato a una extensión mínima de una cuartilla (aprox. 350 palabras).")

    # Clases de palabras
    accuracy = evaluation_results.get("highlights_accuracy")
    if accuracy is not None:
        if accuracy >= 90:
            lineas.append("Has identificado correctamente la mayoría de las clases de palabras.")
        elif accuracy >= 70:
            lineas.append("Revisa adverbios y preposiciones para afianzar su reconocimiento.")
        else:
            lineas.append("Es importante repasar verbos, sustantivos, adjetivos, adverbios, artículos y preposiciones.")

    # Audio
    nv_audio = cog.get("audio", "")
    if nv_audio == "Requiere Apoyo":
        lineas.append("No se encontró la grabación o la liga de acceso al audio. Inclúyela al final del documento.")
    elif nv_audio in ("Capacitado", "Aceptable"):
        lineas.append("Procura que el relato oral tenga entre 2 y 3 minutos.")

    # Reflexión oral/escrito
    nv_parrafo = cog.get("parrafo", "")
    if nv_parrafo in ("Experto", "Capacitado"):
        lineas.append("Escribiste el párrafo sobre las diferencias entre expresión oral y escrita de forma adecuada.")
    else:
        lineas.append("Incluye un párrafo de 5 a 10 líneas sobre las diferencias que encontraste al expresarte por escrito y de forma oral.")

    # Ortografía (los recursos concretos vienen del CSV y se pasan al LLM en recursos_texto)
    errores = com.get("errores_ortografia")
    if errores is not None:
        if errores == 0:
            lineas.append("No presentas errores en sintaxis, ortografía o puntuación.")
        elif errores <= 3:
            lineas.append("Hay algunos errores menores de ortografía o puntuación; recomienda recursos del listado (p. ej. correctores, acentuación).")
        else:
            lineas.append("Se observan varios errores de ortografía y puntuación; recomienda varios recursos del listado para reforzar (LenguageTool, signos de puntuación, acentos).")

    # Originalidad
    if orig.get("deduccion", 0) > 0:
        lineas.append("Incorpora anécdotas y detalles propios para que el relato refleje tu voz personal.")

    return " ".join(lineas)


def _retro_system_instruction():
    """System prompt enviado a Gemini y Ollama (mismo texto en generate_feedback y vista previa)."""
    return (
        "Eres un asesor virtual de Prepa en Línea-SEP. Redacta una retroalimentación personalizada "
        "para la actividad \"Mi Historia de Vida\" (M2 AI2).\n"
        "Usa tono cercano, respetuoso y constructivo. Reconoce el esfuerzo. No uses lenguaje punitivo.\n"
        "Sigue EXACTAMENTE esta estructura: 1) Saludo \"Hola [Nombre]:\"; 2) Apertura (objetivos, netiqueta); "
        "3) Ejercicio 1 – Relato; 4) Ejercicio 2 – Clases de palabras; 5) Ejercicio 3 – Audio/video; "
        "6) Ejercicio 4 – Párrafo oral/escrito; 7) Cumplimiento técnico; 8) Criterio comunicativo (ortografía); "
        "9) Pensamiento crítico; 10) Originalidad (solo si hay deducción); 11) Recursos sugeridos: recomienda "
        "VARIOS recursos de la lista proporcionada según cada necesidad a reforzar; 12) Cierre alentador; "
        "13) \"Saludos,\" + firma.\n"
        "Si relato_titulo es true en el JSON de evaluación, no sugieras cambiar el título: variantes como "
        "\"Mi historia\", \"Relatando mi historia\" o \"El relato de mi historia\" son válidas.\n"
        "Usa frases_sugeridas_mapeo del JSON como guía de qué mencionar o no (no repitas correcciones ya resueltas).\n"
        "Escribe en español de México. Extensión aproximada 400-600 palabras. "
        "Incluye en la sección de recursos al menos 2-3 enlaces distintos del listado según las áreas que el alumno deba reforzar."
    )


def _build_retro_user_content(eval_json, story_snippet, recursos_texto):
    return (
        f"Genera la retroalimentación siguiendo la estructura indicada. "
        f"Escribe solo la retroalimentación, sin explicaciones adicionales.\n\n"
        f"Datos de evaluación (JSON):\n"
        f"{json.dumps(eval_json, ensure_ascii=False, indent=2)}\n\n"
        f"Fragmento del relato (para personalizar):\n"
        f"{story_snippet[:800]}\n\n"
        f"Listado de recursos del Compilado M02 (recomendar varios según la necesidad a reforzar del alumno):\n"
        f"{recursos_texto}"
    )


def build_eval_json_for_llm(evaluation_results, fragmentos, estudiante_nombre="Estudiante", curso="M2", asesor_nombre="Asesor"):
    """Construye el JSON de entrada sugerido en m2_ai2_retroalimentacion.md para el LLM."""
    cog = evaluation_results.get("cognitivo", {})
    act = evaluation_results.get("actitudinal", {})
    com = evaluation_results.get("comunicativo", {})
    pc = evaluation_results.get("pensamiento_critico", {})
    orig = evaluation_results.get("originalidad", {})

    return {
        "estudiante": {"nombre": estudiante_nombre},
        "evaluacion": {
            "cognitivo": {
                "relato_extension": "cumple" if cog.get("relato") == "Experto" else "parcial",
                "relato_titulo": evaluation_results.get("titulo_ok", True),
                "clases_palabras_porcentaje": evaluation_results.get("highlights_accuracy"),
                "audio_presente": evaluation_results.get("audio_found", False),
                "audio_liga_funcional": evaluation_results.get("liga_ok", False),
                "audio_duracion_min": round((evaluation_results.get("audio_duration") or 0) / 60, 1),
                "parrafo_oral_escrito_presente": fragmentos.get("tiene_reflexion", False),
            },
            "actitudinal": {"indicaciones_cumplidas": act.get("cumplidos", 0), "indicaciones_totales": 12},
            "comunicativo": {
                "errores_ortografia": com.get("errores_ortografia"),
                "nivel": com.get("level"),
            },
            "pensamiento_critico": {"nivel": pc.get("level")},
            "originalidad": {"deduccion_puntos": orig.get("deduccion", 0), "nivel": orig.get("nivel")},
            "similitud_relato_audio_alta": evaluation_results.get("similitud_relato_audio_alta", False),
        },
        "curso": curso,
        "asesor": {"nombre": asesor_nombre},
        "fragmentos_para_personalizar": fragmentos,
        "frases_sugeridas_mapeo": _mapeo_frases(evaluation_results),
    }


# Rutas posibles del Compilado M02 (raíz del proyecto o docs/01_guias)
COMPILADO_CSV_CANDIDATES = [
    "Compilado M02_RED_DSAyDC.csv",
    "docs/01_guias/Compilado M02_RED_DSAyDC.csv",
]


class FeedbackGenerator:
    def __init__(self, api_key=None, csv_path=None, ollama_url=None, ollama_model="mistral"):
        self.api_key = (api_key or os.environ.get("GEMINI_API_KEY") or "").strip() or None
        self.ollama_url = (ollama_url or os.environ.get("OLLAMA_URL") or "").strip() or None
        self.ollama_model = ((ollama_model or os.environ.get("OLLAMA_MODEL", "mistral")) or "mistral").strip().strip("_") or "mistral"
        if csv_path and os.path.exists(csv_path):
            self.csv_path = csv_path
        else:
            self.csv_path = None
            for p in COMPILADO_CSV_CANDIDATES:
                if os.path.exists(p):
                    self.csv_path = p
                    break
            self.csv_path = self.csv_path or csv_path or COMPILADO_CSV_CANDIDATES[0]
        self._client_new = None
        if self.api_key and _USE_NEW_GENAI:
            self._client_new = _genai_new.Client(api_key=self.api_key)
        elif self.api_key and _genai_legacy:
            _genai_legacy.configure(api_key=self.api_key)
        self.materials_df = _cargar_compilado(self.csv_path)

    def get_suggested_materials(self, evaluation_results, max_por_area=3, max_total=10):
        """Sugiere varios recursos del Compilado M02 según las áreas que el alumno debe reforzar."""
        areas = []
        cog = evaluation_results.get("cognitivo", {})
        com = evaluation_results.get("comunicativo", {})
        if cog.get("clases") not in ("Experto", "Capacitado"):
            areas.append("clases_palabras")
        if (com.get("errores_ortografia") or 0) > 0:
            areas.append("ortografia")
        if cog.get("parrafo") not in ("Experto", "Capacitado"):
            areas.append("comunicacion_oral_escrita")
        if cog.get("relato") not in ("Experto", "Capacitado"):
            areas.append("redaccion")
        if not areas:
            areas.append("clases_palabras")
        return _sugerir_recursos_por_area(
            self.materials_df, areas, max_por_area=max_por_area, max_total=max_total
        )

    def generate_feedback(
        self,
        evaluation_results,
        story_snippet,
        fragmentos=None,
        student_name="Estudiante",
        curso="M2",
        asesor_nombre="Asesor",
    ):
        """
        Genera retroalimentación con Gemini siguiendo la estructura obligatoria (bloques 1-13)
        y el mapeo de docs/03_data_AI2/m2_ai2_retroalimentacion.md.
        """
        fragmentos = fragmentos or {}
        eval_json = build_eval_json_for_llm(
            evaluation_results, fragmentos, student_name, curso, asesor_nombre
        )
        recursos = self.get_suggested_materials(
            evaluation_results, max_por_area=3, max_total=10
        )
        por_area = {}
        for r in recursos:
            a = r.get("area", "general")
            por_area.setdefault(a, []).append(r)
        recursos_texto = "Recursos disponibles por área de refuerzo (recomienda varios según la necesidad del alumno):\n"
        nombres_area = {
            "clases_palabras": "Clases de palabras / gramática",
            "ortografia": "Ortografía y puntuación",
            "comunicacion_oral_escrita": "Comunicación oral y escrita",
            "redaccion": "Redacción y relato",
            "netiqueta": "Netiqueta",
        }
        for area, items in por_area.items():
            etiqueta = nombres_area.get(area, area)
            recursos_texto += f"\n[{etiqueta}]\n"
            recursos_texto += "\n".join([f"  - {r['nombre']}: {r['url']}" for r in items])

        system_instruction = _retro_system_instruction()
        user_content = _build_retro_user_content(eval_json, story_snippet, recursos_texto)

        # 1) Nuevo SDK Google GenAI (google.genai)
        if self._client_new:
            try:
                from google.genai import types
                config = types.GenerateContentConfig(system_instruction=system_instruction)
                response = self._client_new.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=user_content,
                    config=config,
                )
                text = getattr(response, "text", None) or (response.candidates[0].content.parts[0].text if response.candidates else "")
                return text.strip() if text else str(response)
            except Exception as e:
                return f"Error al generar retroalimentación (Gemini): {str(e)}"

        # 2) Legacy google.generativeai
        if self.api_key and _genai_legacy:
            try:
                model = _genai_legacy.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction)
                response = model.generate_content(user_content)
                return response.text if hasattr(response, "text") else str(response)
            except Exception as e:
                return f"Error al generar retroalimentación: {str(e)}"

        # 3) Ollama como fallback (sin API Key de Gemini)
        ollama_base = self.ollama_url or os.environ.get("OLLAMA_URL", "").strip()
        if ollama_base:
            out = _call_ollama(system_instruction, user_content, url=ollama_base, model=self.ollama_model)
            if out:
                return out
            return "Ollama no respondió. Comprueba que el servicio esté en marcha y que el modelo esté instalado (ej. ollama pull mistral)."

        return "No hay API de Gemini configurada ni Ollama disponible. Configura GEMINI_API_KEY en la barra lateral o la variable OLLAMA_URL (ej. http://host.docker.internal:11434) para usar Ollama."

    def get_prompt_preview(self, evaluation_results, story_snippet, fragmentos=None, student_name="Estudiante", curso="M2", asesor_nombre="Asesor"):
        """
        Devuelve el mismo system + user que generate_feedback envía a Ollama/Gemini.
        La guía humana docs/03_data_AI2/m2_ai2_retroalimentacion.md no se inyecta al modelo.
        """
        fragmentos = fragmentos or {}
        eval_json = build_eval_json_for_llm(
            evaluation_results, fragmentos, student_name, curso, asesor_nombre
        )
        recursos = self.get_suggested_materials(
            evaluation_results, max_por_area=3, max_total=10
        )
        por_area = {}
        for r in recursos:
            a = r.get("area", "general")
            por_area.setdefault(a, []).append(r)
        recursos_texto = "Recursos disponibles por área de refuerzo (recomienda varios según la necesidad del alumno):\n"
        nombres_area = {
            "clases_palabras": "Clases de palabras / gramática",
            "ortografia": "Ortografía y puntuación",
            "comunicacion_oral_escrita": "Comunicación oral y escrita",
            "redaccion": "Redacción y relato",
            "netiqueta": "Netiqueta",
        }
        for area, items in por_area.items():
            etiqueta = nombres_area.get(area, area)
            recursos_texto += f"\n[{etiqueta}]\n"
            recursos_texto += "\n".join([f"  - {r['nombre']}: {r['url']}" for r in items])

        system = _retro_system_instruction()
        user = _build_retro_user_content(eval_json, story_snippet, recursos_texto)

        return (
            "=== SYSTEM (enviado a Ollama/Gemini) ===\n\n"
            + system
            + "\n\n=== USER (con datos de esta evaluación) ===\n\n"
            + user
        )
