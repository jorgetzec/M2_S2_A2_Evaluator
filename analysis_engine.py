import os
import re
import json
import requests
import spacy
from faster_whisper import WhisperModel
import tempfile

# Attempt to load spaCy
try:
    nlp = spacy.load("es_core_news_sm")
except:
    nlp = None

def _word_looks_like_verb(word):
    """
    Heurística para casos donde spaCy suele etiquetar mal como PROPN, NOUN o DET
    palabras que en realidad son verbos conjugados al inicio de oración o aisladas.
    """
    if not word:
        return False
    low = word.strip().lower()
    if len(low) < 2:
        return False
    
    # Lista de verbos comunes irregulares o problemáticos para spaCy
    common_irr = {"veo", "soy", "voy", "fui", "iba", "ver", "dar", "ir"}
    if low in common_irr:
        return True
        
    # Terminaciones verbales típicas (Pretérito, Imperfecto, Presente 1ra pers)
    verb_endings = (
        "í", "é", "ó", "aste", "iste", "uyó", "uieron",
        "aba", "abas", "abamos", "aban",
        "ía", "ías", "íamos", "ían",
        "iremos", "eremos", "aremos",
        "ré", "rás", "rá", "rem", "rán"
    )
    return low.endswith(verb_endings)

def _lemma_looks_verb(lemma: str) -> bool:
    """Heurística simple: infinitivos (-ar/-er/-ir)."""
    if not lemma:
        return False
    low = str(lemma).strip().lower()
    return low.endswith("ar") or low.endswith("er") or low.endswith("ir")


def _word_looks_like_noun(word: str) -> bool:
    """Heurística simple para sustantivos frecuentes en español."""
    if not word:
        return False
    low = str(word).strip().lower()
    if len(low) < 3:
        return False
    noun_suffixes = (
        "ción", "sión", "dad", "tad", "ez", "eza", "ncia", "ncias",
        "umbre", "miento", "mientos", "aje", "ajes", "ura", "uras",
    )
    return low.endswith(noun_suffixes)


def _is_participle(word: str) -> bool:
    """Detecta si una palabra tiene terminación de participio (-ado, -ido, -ada, -ida)."""
    if not word or len(word) < 4:
        return False
    low = word.strip().lower()
    return low.endswith(("ado", "ido", "ada", "ida"))

def pos_matches_category(pos_detected, category, word=None):
    """Checks if detected POS matches the pedagogical category (with heuristics)."""
    if pos_detected == category:
        return True
    if category == "VERB":
        if pos_detected in ("AUX", "VERB"):
            return True
        # Caso especial: Participios (que Spacy suele ver como ADJ) aceptados como VERB
        if pos_detected == "ADJ" and _is_participle(word):
            return True
        # Caso especial: spaCy puede etiquetar verbos conjugados con letra inicial en mayúscula como PROPN.
        if pos_detected == "PROPN" and _word_looks_like_verb(word):
            return True
    if category == "NOUN" and pos_detected in ("NOUN", "PROPN", "PRON"):
        # Se acepta PRON como NOUN porque la rúbrica no tiene categoría Pronombre
        # y los estudiantes los usan como núcleos del sujeto.
        return True
    if category == "ADJ" and pos_detected in ("ADJ", "DET", "PRON"):
        return True
    if category == "ADJ" and pos_detected == "ADV":
        # En tareas escolares algunos adjetivos/adverbios limítrofes (p. ej. "cerca")
        # pueden variar por contexto; no penalizamos este caso.
        return True
    if category == "DET" and pos_detected in ("DET", "PRON"):
        return True
    if category == "ADP" and pos_detected in ("ADP", "SCONJ"):
        return True
    return False

def validate_highlights(highlights):
    """Validates a list of highlights (word, expected_category) using spaCy."""
    results = []
    correct = 0
    map_expected = {
        "SUSTANTIVO": "NOUN",
        "VERBO": "VERB",
        "ADJETIVO": "ADJ",
        "ADVERBIO": "ADV",
        "ARTICULO": "DET",
        "ARTÍCULO": "DET",
        "PREPOSICION": "ADP",
        "PREPOSICIÓN": "ADP",
    }
    for h in highlights:
        word = str(h["word"]).strip()
        # Ignorar números puros (no son clases de palabras evaluables en esta rúbrica)
        if word.isdigit():
            continue
            
        expected_raw = str(h.get("expected_category", "")).strip().upper()
        expected = map_expected.get(expected_raw, expected_raw)
        pos = get_word_class(word)

        token_lemma = None
        if nlp and word and isinstance(word, str):
            try:
                clean = re.sub(r"[^\w\s]", "", word).strip()
                doc = nlp(clean) if clean else None
                if doc and len(doc) > 0:
                    token_lemma = doc[0].lemma_
            except Exception:
                token_lemma = None

        # Ajuste adicional: si spaCy etiquetó como PROPN, NOUN o DET pero el esperado es VERB,
        # probamos clasificando la palabra en minúsculas (caso típico al inicio de oración)
        # o usando heurísticas (caso típico de palabras aisladas que pierden contexto).
        if expected == "VERB" and pos not in ("AUX", "VERB"):
            pos_lower = get_word_class(word.lower())
            if pos_lower in ("AUX", "VERB"):
                pos = pos_lower
            # Si aún no es VERB pero "parece" verbo (ej: "veo", "crecí"), lo aceptamos.
            elif _lemma_looks_verb(token_lemma) or _word_looks_like_verb(word):
                pos = "VERB"

        # Ajuste: evitar falsos VERB para sustantivos comunes (p. ej. "niñez").
        if expected == "NOUN":
            if pos == "VERB":
                if token_lemma and not _lemma_looks_verb(token_lemma):
                    pos = "NOUN"
                elif _word_looks_like_noun(word):
                    pos = "NOUN"
            elif _word_looks_like_noun(word) and pos not in ("NOUN", "PROPN"):
                pos = "NOUN"

        # Para evitar falsos negativos visuales en tabla, normalizamos la etiqueta detectada
        # cuando el caso es aceptado por la heurística pedagógica.
        if expected == "ADJ" and pos == "ADV":
            pos = "ADJ"

        match = pos_matches_category(pos, expected, word=word)
        if match: correct += 1
        results.append({
            "word": word,
            "expected": expected,
            "detected": pos,
            "match": match
        })
    
    accuracy = (correct / len(highlights) * 100) if highlights else 0
    return {
        "details": results,
        "total": len(highlights),
        "correct": correct,
        "accuracy": round(accuracy, 1)
    }

def get_word_class(text):
    if not nlp or not text.strip():
        return "Unknown"
    clean_text = re.sub(r'[^\w\s]', '', text)
    if not clean_text:
        return "Punct"
    doc = nlp(clean_text)
    if len(doc) > 0:
        return doc[0].pos_
    return "Unknown"

def count_words(text):
    if not text:
        return 0
    return len(text.split())

def check_orthography(text):
    """Hits LanguageTool API."""
    if not text:
        return 0, []
    try:
        url = "https://api.languagetool.org/v2/check"
        data = {"text": text, "language": "es"}
        resp = requests.post(url, data=data, timeout=15)
        result = resp.json()
        matches = result.get("matches", [])
        details = []
        for m in matches:
            details.append({
                "message": m.get("message"),
                "context": m.get("context", {}).get("text"),
                "suggestion": m.get("replacements", [{}])[0].get("value", "") if m.get("replacements") else ""
            })
        return len(matches), details
    except:
        return None, []

def transcribe_audio(audio_path, model_size="base"):
    """Transcribe using faster-whisper."""
    if not audio_path or not os.path.isfile(audio_path):
        return "", 0
    try:
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_path, language="es")
        text = " ".join(s.text for s in segments).strip()
        duration = info.duration
        return text, duration
    except Exception as e:
        return str(e), 0


def _extract_google_drive_id(url):
    import re as _re
    m = _re.search(r"/file/d/([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1)
    m = _re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1)
    m = _re.search(r"/open\?id=([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1)
    return None


def _dropbox_direct_url(url):
    if "?dl=0" in url:
        return url.replace("?dl=0", "?dl=1")
    if "?" in url and "dl=1" not in url:
        return url + "&dl=1"
    return url + "?dl=1" if "?" not in url else url


def download_audio_from_url(audio_url, dest_dir=None):
    """
    Descarga audio desde enlaces comunes y devuelve (ruta_local, error).
    Inspirado en docs/04_old_version/audio_transcribe.py.
    """
    if not audio_url or not str(audio_url).strip():
        return None, "URL vacía"
    dest_dir = dest_dir or tempfile.gettempdir()
    os.makedirs(dest_dir, exist_ok=True)
    out_base = os.path.join(dest_dir, "audio_descargado")

    url = str(audio_url).strip()

    def _perm_hint(msg: str) -> str:
        if not msg:
            return msg
        low = msg.lower()
        if "privad" in low or "permiso" in low or "permission" in low or "forbidden" in low or "unauthorized" in low:
            return "Enlace privado o sin permisos. Solicita acceso o configura el archivo como 'Cualquier persona con el enlace'."
        if "gdown" in low:
            return "Drive requiere descarga directa o gdown; si el archivo es privado, también requiere permisos."
        return msg

    # Google Drive
    if "drive.google.com" in url:
        file_id = _extract_google_drive_id(url)
        if not file_id:
            return None, _perm_hint("No se pudo extraer el ID de Google Drive")
        try:
            import gdown  # type: ignore
            full_url = f"https://drive.google.com/uc?id={file_id}"
            out_path = gdown.download(full_url, out_base, quiet=True, fuzzy=True)
            if not out_path:
                return None, _perm_hint("gdown no pudo descargar (posible enlace privado)")
            return out_path, None
        except Exception:
            # Fallback: intento directo (puede fallar en algunos casos)
            direct = f"https://drive.google.com/uc?export=download&id={file_id}"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(direct, timeout=60, headers=headers, allow_redirects=True)
            resp.raise_for_status()
            data = resp.content
            if b"<!DOCTYPE" in data[:500] or b"<html" in data[:200].lower():
                return None, _perm_hint("Drive requiere gdown o enlace descargable")
            # Intenta inferir extensión mínima
            out_path = out_base + ".mp3"
            with open(out_path, "wb") as f:
                f.write(data)
            return out_path, None

    # Dropbox
    if "dropbox.com" in url:
        direct = _dropbox_direct_url(url)
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(direct, timeout=60, stream=True, headers=headers, allow_redirects=True)
        r.raise_for_status()
        # Intenta extensión desde headers (si existe)
        ext = ".mp3"
        cd = r.headers.get("content-disposition", "")
        # Si no se puede parsear, dejamos mp3.
        if "filename=" in cd:
            import re as _re
            m = _re.findall(r"filename\*?=[\"']?([^\"';]+)", cd)
            if m:
                fname = m[-1]
                ext_guess = os.path.splitext(fname)[1]
                if ext_guess:
                    ext = ext_guess
        out_path = out_base + ext
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return out_path, None

    # OneDrive / URLs directas
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, timeout=60, stream=True, headers=headers, allow_redirects=True)
    r.raise_for_status()
    ext = ".mp3"
    disp = r.headers.get("content-disposition", "")
    if "filename" in disp:
        import re as _re
        m = _re.findall(r"filename\*?=[\"']?([^\"';]+)", disp)
        if m:
            ext_guess = os.path.splitext(m[-1])[1]
            if ext_guess:
                ext = ext_guess
    out_path = out_base + ext
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    return out_path, None


def transcribe_audio_url(audio_url, model_size="base"):
    """
    Descarga el audio desde la URL y transcribe con faster-whisper.
    Retorna (text, duration_seconds, error_message).
    """
    audio_path, err = download_audio_from_url(audio_url, dest_dir=tempfile.gettempdir())
    if err or not audio_path:
        return "", 0.0, f"Descarga: {err or 'no se pudo descargar'}"
    try:
        text, duration = transcribe_audio(audio_path, model_size=model_size)
        # transcribe_audio devuelve (str, duration); duration puede ser 0 si falla.
        text_str = text if isinstance(text, str) else str(text)
        if not text_str.strip():
            return "", float(duration or 0.0), "Transcripción vacía"
        return text_str, float(duration or 0.0), None
    finally:
        try:
            if audio_path and os.path.isfile(audio_path):
                os.remove(audio_path)
        except Exception:
            pass

def _extract_ngrams(text, n=5):
    """Extrae n-gramas de palabras para detectar fragmentos idénticos."""
    if not text:
        return []
    words = text.lower().split()
    return [" ".join(words[i:i + n]) for i in range(len(words) - n + 1)]

def analyze_story_vs_transcription(story_text, transcription_text):
    """Compara relato escrito vs transcripción. Detecta similitud y fragmentos idénticos (evitar lectura)."""
    if not story_text or not transcription_text:
        return {"similarity": 0, "identical_fragments": [], "is_suspicious": False}

    story_words = story_text.lower().split()
    trans_words = transcription_text.lower().split()
    if not story_words:
        return {"similarity": 0, "identical_fragments": [], "is_suspicious": False}

    # Similitud por palabras en común
    set_story = set(story_words)
    set_trans = set(trans_words)
    intersection = set_story.intersection(set_trans)
    similarity_pct = len(intersection) / len(set_story) * 100 if set_story else 0

    # Fragmentos idénticos (5-gramas que aparecen en ambos)
    n = 5
    story_ngrams = set(_extract_ngrams(story_text, n))
    trans_ngrams = set(_extract_ngrams(transcription_text, n))
    identical = list(story_ngrams.intersection(trans_ngrams))[:10]  # Máximo 10 ejemplos

    return {
        "similarity": round(similarity_pct, 1),
        "identical_fragments": identical,
        "is_suspicious": similarity_pct > 75 or len(identical) >= 3,
    }


def build_fragmentos_retro(relato_text, reflexion_text, transcripcion_text, max_chars=500):
    """
    Extrae fragmentos por segmento para generar retroalimentación personalizada.
    Retorna dict con snippets truncados para el LLM.
    """
    def _snippet(t, limit):
        if not t or not isinstance(t, str):
            return ""
        t = t.strip()
        return t[:limit] + "..." if len(t) > limit else t

    return {
        "historia_snippet": _snippet(relato_text, max_chars),
        "reflexion_snippet": _snippet(reflexion_text, max_chars // 2),
        "transcripcion_snippet": _snippet(transcripcion_text, max_chars),
        "tiene_historia": len((relato_text or "").strip()) > 50,
        "tiene_reflexion": len((reflexion_text or "").strip()) > 15,
        "tiene_transcripcion": len((transcripcion_text or "").strip()) > 30,
    }

def detect_ai_indicators(text):
    # Reuse the logic from the user's ai_indicators.py
    frases_tipicas = [
        "en conclusión", "es importante mencionar", "a lo largo de mi vida",
        "en resumen", "cabe destacar", "es fundamental", "no obstante"
    ]
    count = 0
    found = []
    for f in frases_tipicas:
        if f in text.lower():
            count += 1
            found.append(f)
    return {"count": count, "found": found}
