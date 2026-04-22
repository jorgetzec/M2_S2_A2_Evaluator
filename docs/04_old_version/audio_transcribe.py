"""
Descarga de audio desde enlaces de Google Drive, OneDrive, Dropbox, etc.
y transcripción con faster-whisper (español).
"""
import os
import re
import tempfile
import urllib.request
import urllib.parse

# Opcional: gdown para Google Drive (mejor manejo de archivos grandes)
try:
    import gdown
    HAS_GDOWN = True
except ImportError:
    HAS_GDOWN = False

# Opcional: requests para descargas con redirects
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Transcripción
try:
    from faster_whisper import WhisperModel
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False


def _extract_google_drive_id(url):
    """Extrae el file ID de una URL de Google Drive."""
    m = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
    if m:
        return m.group(1)
    m = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', url)
    if m:
        return m.group(1)
    m = re.search(r'/open\?id=([a-zA-Z0-9_-]+)', url)
    if m:
        return m.group(1)
    return None


def _is_google_drive(url):
    return "drive.google.com" in url


def _is_dropbox(url):
    return "dropbox.com" in url


def _is_onedrive(url):
    return "onedrive.live.com" in url or "1drv.ms" in url


def _dropbox_direct_url(url):
    """Convierte enlace de Dropbox a descarga directa."""
    if "?dl=0" in url:
        return url.replace("?dl=0", "?dl=1")
    if "?" in url and "dl=1" not in url:
        return url + "&dl=1"
    return url + "?dl=1" if "?" not in url else url


def download_audio(url, dest_dir=None):
    """
    Descarga un archivo de audio desde URL (Drive, Dropbox, OneDrive o directa).
    Devuelve la ruta del archivo local o None si falla.
    """
    if not url or not url.strip():
        return None, "URL vacía"
    url = url.strip()
    dest_dir = dest_dir or tempfile.gettempdir()
    os.makedirs(dest_dir, exist_ok=True)
    out_path = os.path.join(dest_dir, "audio_descargado")

    try:
        if _is_google_drive(url):
            file_id = _extract_google_drive_id(url)
            if not file_id:
                return None, "No se pudo extraer el ID de Google Drive"
            if HAS_GDOWN:
                # gdown maneja bien archivos grandes y restricciones
                full_url = f"https://drive.google.com/uc?id={file_id}"
                result = gdown.download(full_url, out_path, quiet=True, fuzzy=True)
                if result is None:
                    return None, "gdown no pudo descargar (enlace puede ser privado)"
                return result, None
            else:
                # Fallback: URL directa (puede fallar con archivos grandes)
                direct = f"https://drive.google.com/uc?export=download&id={file_id}"
                req = urllib.request.Request(direct, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = r.read()
                    # Si Google devuelve HTML (confirmación de virus), no es el archivo
                    if b"<!DOCTYPE" in data[:500] or b"<html" in data[:200].lower():
                        return None, "Enlace de Drive requiere gdown (pip install gdown)"
                    with open(out_path, "wb") as f:
                        f.write(data)
                return out_path, None

        if _is_dropbox(url):
            direct = _dropbox_direct_url(url)
            if HAS_REQUESTS:
                r = requests.get(direct, timeout=60, stream=True)
                r.raise_for_status()
                ext = ".mp3"
                if "content-disposition" in r.headers:
                    cd = r.headers["content-disposition"]
                    if "filename=" in cd:
                        ext = os.path.splitext(re.findall(r'filename[*]?=["\']?([^"\']+)', cd)[-1])[1] or ".mp3"
                out_path = out_path + ext
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
                return out_path, None
            else:
                with urllib.request.urlopen(urllib.request.Request(direct, headers={"User-Agent": "Mozilla/5.0"}), timeout=60) as r:
                    out_path = out_path + ".mp3"
                    with open(out_path, "wb") as f:
                        f.write(r.read())
                return out_path, None

        # OneDrive, enlaces directos o cualquier otra URL
        if HAS_REQUESTS:
            r = requests.get(url, timeout=60, stream=True, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            disp = r.headers.get("content-disposition")
            ext = ".mp3"
            if disp and "filename=" in disp:
                ext = os.path.splitext(re.findall(r'filename[*]?=["\']?([^"\';]+)', disp)[-1])[1] or ".mp3"
            out_path = out_path + ext
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            return out_path, None
        else:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                out_path = out_path + ".mp3"
                with open(out_path, "wb") as f:
                    f.write(r.read())
            return out_path, None

    except Exception as e:
        return None, str(e)


def _ensure_wav_for_whisper(path):
    """Convierte a WAV mono 16kHz si hace falta (Whisper trabaja bien con varios formatos; opcional)."""
    try:
        import subprocess
        out = path + ".wav" if not path.lower().endswith(".wav") else path
        if not path.lower().endswith(".wav"):
            subprocess.run([
                "ffmpeg", "-y", "-i", path, "-acodec", "pcm_s16le", "-ac", "1", "-ar", "16000", out
            ], check=True, capture_output=True)
            return out
        return path
    except Exception:
        return path


def transcribe_audio(audio_path, language="es", model_size="base"):
    """
    Transcribe un archivo de audio con faster-whisper.
    Devuelve {"text": "...", "error": None} o {"text": "", "error": "..."}.
    """
    if not HAS_WHISPER:
        return {"text": "", "error": "faster-whisper no instalado (pip install faster-whisper)"}
    if not audio_path or not os.path.isfile(audio_path):
        return {"text": "", "error": "Archivo de audio no encontrado"}
    try:
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_path, language=language or "es", beam_size=1)
        text = " ".join(s.text for s in segments).strip()
        return {"text": text, "error": None}
    except Exception as e:
        return {"text": "", "error": str(e)}


def get_audio_duration_seconds(audio_path):
    """Obtiene la duración en segundos con ffprobe (2-3 min = 120-180 s para la rúbrica)."""
    try:
        import subprocess
        out = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", audio_path
        ], capture_output=True, text=True, timeout=10)
        if out.returncode == 0 and out.stdout.strip():
            return float(out.stdout.strip())
    except Exception:
        pass
    return None


def download_and_transcribe(audio_url, dest_dir=None, language="es", model_size="base"):
    """
    Descarga el audio desde la URL y lo transcribe.
    Devuelve {"text": "...", "error": None, "downloaded_path": "...", "duration_seconds": N} o error en "error".
    """
    path, err = download_audio(audio_url, dest_dir=dest_dir)
    if err:
        return {"text": "", "error": f"Descarga: {err}", "downloaded_path": None, "duration_seconds": None}
    duration_seconds = get_audio_duration_seconds(path)
    try:
        result = transcribe_audio(path, language=language, model_size=model_size)
        result["downloaded_path"] = path
        result["duration_seconds"] = duration_seconds
        return result
    finally:
        try:
            if path and os.path.isfile(path):
                os.remove(path)
        except Exception:
            pass
