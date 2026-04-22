# Evaluador M2 AI2 – Mi Historia de Vida

Aplicación **Streamlit** para automatizar la evaluación de la Actividad Integradora 2 del Módulo 2 (Prepa en Línea-SEP). Sustituye el flujo anterior en n8n por una interfaz con GUI que permite subir entregas en varios formatos, segmentar el documento, aplicar la rúbrica y generar retroalimentación con IA.

## Requisitos

- **Python 3.10+**
- **Tesseract OCR** (para imágenes) y **FFmpeg** (para video/audio), si se usan esos formatos
- **Gemini API Key** (opcional, solo para generar retroalimentación con IA)
- **Ollama** (opcional, solo para generar retroalimentación sin Gemini)

## Ollama (opcional)
Si quieres que la retroalimentación se genere con un modelo local (sin Gemini), instala y ejecuta Ollama:

```bash
# Inicia el servidor
ollama serve

# Descarga un modelo (ejemplo)
ollama pull mistral

# Lista modelos disponibles
ollama list
```

Cuando uses la app dentro de Docker, el contenedor debe poder llegar al puerto de Ollama.
En Windows normalmente usa `http://host.docker.internal:11434`.

## Inicio rápido

### 1. Clonar o abrir el proyecto

```bash
cd "D:\CODE\Code3_Coding and Data\20260318_M02S1AI2_app_evaluador"
```

### 2. Entorno virtual (recomendado)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
python -m spacy download es_core_news_sm
```

### 4. Ejecutar la aplicación

```bash
streamlit run app.py
```

Se abrirá en el navegador en `http://localhost:8501`.

---

## Uso con Docker

Si prefieres no instalar Python ni Tesseract/FFmpeg en tu máquina:

```bash
# Primera vez (construir la imagen y levantar en primer plano: menú de streamlit)
docker compose up --build

# Primera vez (construir la imagen y levantar en segundo plano)
docker compose up --build -d
```

### Comandos útiles
```bash
# Ver logs
docker compose logs -f evaluador_app

# Parar contenedores sin borrarlos
docker compose stop

# Borrar contenedores, red y volúmenes (si aplica)
docker compose down
```

### ¿Por qué parece que la terminal se “queda en un menú”?
Cuando ejecutas `docker compose up --build` **sin** `-d`, Docker se queda en **primer plano** mostrando logs/eventos, y por eso no puedes escribir otros comandos en esa misma terminal (es normal).

Solución: usa `-d` (como `docker compose up --build -d`) y consulta logs con `docker compose logs -f ...`.

La app quedará en `http://localhost:8501`. El volumen montado (`.:/app`) permite que los cambios en el código se reflejen al recargar.

---

## Configuración

- **Gemini API Key**: En la barra lateral de la app, introduce tu API Key de Google Gemini para poder generar la retroalimentación automática. Si está vacía, la app puede usar **Ollama** (si está configurado).
- **Compilado de recursos**: La app usa el CSV `Compilado M02_RED_DSAyDC.csv` para recomendar recursos por área de mejora (clases de palabras, ortografía, comunicación oral/escrita, etc.). Busca el archivo en:
  - raíz del proyecto: `Compilado M02_RED_DSAyDC.csv`
  - o en `docs/01_guias/Compilado M02_RED_DSAyDC.csv`

- **Ollama URL y modelo (opcional)**: Si vas a generar la retro sin Gemini, configura en la barra lateral:
  - `Ollama URL`: en Docker normalmente `http://host.docker.internal:11434`
  - `Modelo Ollama`: por defecto `mistral`

## Flujo de trabajo

1. **Subir archivo**: DOCX, PDF, PPTX, imagen (PNG/JPG), video (MP4) o audio (MP3/WAV).
2. **Revisar extracción**: Vista previa del texto y, si aplica, detección de título, fuente y enlace al audio.
3. **Segmentar**: Indicar qué parte es el relato (Ejercicio 1), el párrafo de reflexión (Ejercicio 4) y corregir el enlace al audio (Ejercicio 3) si hace falta.
4. **Ejecutar análisis**: Conteo de palabras, clases de palabras (colores en Word), ortografía (LanguageTool), transcripción de audio (Whisper), similitud texto/audio, indicadores de IA.
5. **Generar evaluación**: Se aplica la rúbrica M2 AI2 (cognitivo, actitudinal, comunicativo, pensamiento crítico, originalidad).
6. **Generar retroalimentación**: Con Gemini se genera un texto siguiendo la plantilla oficial; se recomiendan **varios recursos** del Compilado según lo que el alumno deba reforzar.
7. **Descargar**: JSON o TOON con el resultado completo.

## Estructura del proyecto

```
├── app.py                 # Interfaz Streamlit
├── file_processor.py      # Extracción de texto (Word, PDF, PPTX, imagen, audio/video)
├── analysis_engine.py     # Métricas (palabras, ortografía, highlights, Whisper, similitud)
├── evaluator.py           # Rúbrica M2 AI2 y export JSON/TOON
├── feedback_generator.py  # Retroalimentación con Gemini y recursos del CSV
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Compilado M02_RED_DSAyDC.csv   # Recursos recomendados por área
└── docs/
    ├── 01_guias/
    ├── 02_bitacoras/
    ├── 03_data_AI2/       # Rúbrica, métricas, plantilla de retroalimentación
    └── 04_old_version/    # Scripts antiguos (n8n / processor v4)
```

## Documentación de referencia

- Rúbrica y métricas: `docs/03_data_AI2/m2_ai2_rubrica.md`, `m2_ai2_metricas_evaluacion.md`
- Plantilla de retroalimentación: `docs/03_data_AI2/m2_ai2_retroalimentacion.md`
- Descripción de la actividad: `docs/03_data_AI2/m2_ai2_mi_historia.md`

## Licencia

Uso interno / educativo Prepa en Línea-SEP.
