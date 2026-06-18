# Evaluador M2 AI2

Aplicación **Streamlit** para asistir la evaluación de la actividad integradora **M2 AI2**. Permite subir entregas en varios formatos, segmentar el documento, aplicar la rúbrica y generar retroalimentación con IA (Gemini u Ollama).

## Requisitos

- **Python 3.10+**
- **Tesseract OCR** (imágenes) y **FFmpeg** (video/audio), si usas esos formatos
- **Gemini API Key** (opcional, para retroalimentación con IA en la nube)
- **Ollama** (opcional, retroalimentación local sin Gemini)

## Ollama (opcional)

```bash
ollama serve
ollama pull mistral
ollama list
```

En Docker, el contenedor debe alcanzar Ollama en el host. En Windows suele ser `http://host.docker.internal:11434`.

## Inicio rápido

### Entorno local

```bash
cd <ruta-del-proyecto>
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
python -m spacy download es_core_news_sm
streamlit run app.py
```

La app se abre en `http://localhost:8501`.

### Docker

```bash
# Construir y levantar en segundo plano
docker compose up --build -d

# Ver logs
docker compose logs -f evaluador_app

# Detener
docker compose stop
docker compose down
```

Si ejecutas `docker compose up --build` **sin** `-d`, la terminal queda mostrando logs (es normal). Usa `-d` y consulta logs con `docker compose logs -f`.

Con el volumen `.:/app`, los cambios en código se reflejan al recargar la página.

## Configuración

| Opción | Dónde | Descripción |
|--------|--------|-------------|
| Gemini API Key | Barra lateral de la app | Retroalimentación con Gemini. Alternativa: Ollama. |
| `GEMINI_API_KEY` | Variable de entorno | Misma clave, sin pegarla en la UI. |
| Ollama URL | Barra lateral | Por defecto en Docker: `http://host.docker.internal:11434` |
| `OLLAMA_URL`, `OLLAMA_MODEL` | Variables de entorno | URL y modelo (por defecto `mistral`). |
| Compilado de recursos | CSV en el proyecto | `Compilado M02_RED_DSAyDC.csv` (raíz o `docs/01_guias/`). |

No subas claves ni `.env` al repositorio; usa `.gitignore` y variables de entorno.

## Flujo de trabajo

1. **Subir archivo**: DOCX, PDF, PPTX, imagen (PNG/JPG), video (MP4) o audio (MP3/WAV).
2. **Vista previa y segmentación**: Relato (ej. 1), reflexión (ej. 4), enlace al audio (ej. 3).
3. **Ejecutar análisis**: Palabras, clases de palabras (sombreado en DOCX/PDF/PPTX/imagen/video), ortografía (LanguageTool), transcripción (Whisper), similitud relato/audio.
4. **Generar evaluación**: Rúbrica (cognitivo, actitudinal, comunicativo, pensamiento crítico, originalidad).
5. **Retroalimentación**: Texto según plantilla + recursos del compilado.
6. **Exportar**: JSON con métricas, fragmentos, indicadores y retro.

### Audio desde enlaces en la nube

La app intenta descargar y transcribir desde:

- **Google Drive** (`gdown` o descarga directa)
- **Dropbox** (`?dl=1`)
- **OneDrive / 1drv.ms** (token Badger + API Microsoft)
- **SharePoint** (`?download=1`)

**OneDrive**

1. Compartir como **«Cualquier persona con el vínculo»** (sin exigir inicio de sesión).
2. Preferir el enlace corto `https://1drv.ms/...` (incluye formatos `/u/s!...` y `/u/c/...`).
3. Prueba:

```bash
docker compose exec evaluador_app python scratch/test_onedrive.py "https://1drv.ms/..."
```

La transcripción de audios largos puede tardar varios minutos.

## Estructura del proyecto

```
├── app.py                 # Interfaz Streamlit
├── file_processor.py      # Texto, resaltados y segmentación
├── analysis_engine.py     # Métricas, Whisper, descarga de audio por URL
├── evaluator.py           # Rúbrica y export JSON
├── feedback_generator.py  # Retroalimentación (Gemini / Ollama)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── scratch/               # Scripts de prueba (no datos de alumnos)
└── docs/
    ├── 01_guias/
    ├── 02_bitacoras/
    ├── 03_data_AI2/       # Rúbrica, métricas, plantilla de retro
    └── 04_old_version/    # Referencia de implementaciones anteriores
```

## Documentación de referencia

- Rúbrica y métricas: `docs/03_data_AI2/m2_ai2_rubrica.md`, `m2_ai2_metricas_evaluacion.md`
- Plantilla de retroalimentación: `docs/03_data_AI2/m2_ai2_retroalimentacion.md`
- Descripción de la actividad: `docs/03_data_AI2/m2_ai2_mi_historia.md`

## Licencia

Uso interno y educativo.
