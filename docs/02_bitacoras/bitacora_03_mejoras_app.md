# Bitácora | Mejoras en la App Evaluadora
## 2026-03-18 - Resumen de mejoras funcionales (M2 AI2)

**Files**: `file_processor.py`, `evaluator.py`, `analysis_engine.py`, `feedback_generator.py`, `app.py`  
**Tags**: #streamlit #evaluacion #ocr #transcripcion #segmentacion #ia #gemini
**Objective**: Consolidar la extracción de entregas, métricas, rúbrica M2 AI2 y retroalimentación estructurada con IA; además de mejorar la UX del asesor con segmentación y export.

### Descripción del Proceso

**file_processor.py**
Extracción de enlace de audio: `extract_audio_url_from_text()` detecta URLs (Drive, Dropbox, YouTube, etc.) en el texto, sobre todo al final del documento. Detección de título: `detect_titulo_presente()` comprueba si aparece “El relato de mi historia”. Detección de fuente: en DOCX, `_check_fuente_arial_12_docx()` comprueba Arial 12 pt en los primeros párrafos. Meta en la salida: el procesador devuelve un 5º elemento `meta` con `titulo_ok`, `fuente_ok` y `audio_url` (también para PDF/PPTX/imagen usando el texto extraído).

**evaluator.py (rúbrica completa)**
Cognitivo: nivel por extensión del relato (350–1000 palabras) y por título/fuente; nivel global cognitivo como en la rúbrica v4; audio 2–3 min (120–180 s). Actitudinal: 12 indicaciones explícitas guardadas en indicadores y cumplidos. Comunicativo: nivel según errores de ortografía (0, 1–3, 4–5, 6–8, >8). Pensamiento crítico: nivel según acierto en clases de palabras y párrafo de reflexión. Originalidad: deducción por indicadores de IA y por similitud alta texto/audio (posible lectura). Export: JSON completo y TOON con `s, cog, act, com, pc, orig, ded`.

**analysis_engine.py**
Similitud texto/audio: devuelve `identical_fragments` (n-gramas repetidos) e `is_suspicious` (similitud >75% o varios fragmentos idénticos). Fragmentos para retro: `build_fragmentos_retro()` genera snippets de relato, reflexión y transcripción para el LLM.

**feedback_generator.py**
Estructura tipo M2 AI2: instrucciones para el LLM con los 13 bloques (saludo, ejercicios 1–4, cumplimiento, comunicativo, pensamiento crítico, originalidad, recurso, cierre, despedida). Mapeo de métricas a frases: uso de las frases sugeridas del doc de retroalimentación según el resultado de cada criterio. Recursos por área: uso del CSV `Compilado M02_RED_DSAyDC.csv` filtrado por área (clases de palabras, ortografía, comunicación oral/escrita, redacción) para sugerir enlaces. Entrada al LLM: JSON de evaluación en el formato del doc (estudiante, evaluación por criterio, fragmentos, frases sugeridas).

**app.py**
Segmentación por ejercicios: panel con “Ejercicio 1 – Relato”, “Ejercicio 2 – Clases de palabras” (informativo), “Ejercicio 3 – Enlace al audio” (editable), “Ejercicio 4 – Párrafo de reflexión”. Enlace al audio: se rellena con la URL detectada en el texto y se puede corregir manualmente. Meta visible: se muestra si se detectó título y fuente Arial 12. Evaluación manual: expander “Evaluación manual” con puntaje total y observaciones cuando el formato no se puede procesar o se prefiere evaluar a mano. Uso de fragmentos: al generar la retroalimentación se envían los fragmentos de cada segmento al generador. Resultados: se muestran nivel cognitivo global, originalidad y deducción; descarga JSON/TOON con la evaluación completa.

---


## 2026-03-18 - Recursos recomendados y README

**Files**: `feedback_generator.py`, `README.md`  
**Objective**: Ajustar la selección de recursos del CSV (varios enlaces por área) y documentar el uso del proyecto (incluyendo Docker).

### Descripción del Proceso

**Resumen de los cambios**

**1) Recursos recomendados según necesidad (`feedback_generator.py`)**
- `_sugerir_recursos_por_area` ahora puede devolver hasta 3 recursos por área y 10 en total, usando el CSV `Compilado M02_RED_DSAyDC.csv`.
- Áreas y palabras clave: se ampliaron las búsquedas (p. ej. `"categoria gramatical"`, `"oralidadYescritura"`, `"reglas ortográficas"`, `"secuencia del relato"`) para alinearlas mejor con las columnas del CSV.
- Listado por área para el LLM: los recursos se agrupan por área (Clases de palabras, Ortografía, Comunicación oral y escrita, Redacción) y se pasan al modelo con la instrucción de recomendar varios según lo que el alumno deba reforzar.
- Ortografía: en el mapeo de frases se deja de recomendar solo `LenguageTool`; se indica que use “recursos del listado” (correctores, acentos, puntuación) que vienen del CSV.
- Dónde se busca el CSV: se intenta cargar el Compilado desde la raíz del proyecto (`Compilado M02_RED_DSAyDC.csv`) o desde `docs/01_guias/Compilado M02_RED_DSAyDC.csv`, y se probaron varios encodings (`utf-8`, `latin-1`, `cp1252`).
- El prompt del LLM pide explícitamente: “recomienda VARIOS recursos de la lista proporcionada según cada necesidad a reforzar” e “incluye en la sección de recursos al menos 2-3 enlaces distintos del listado”.

**2) `README.md` del proyecto**
Se creó `README.md` en la raíz con:
- Descripción del proyecto (Evaluador M2 AI2, sustitución del flujo n8n).
- Requisitos: Python 3.10+, Tesseract/FFmpeg opcionales, API Key de Gemini opcional.
- Inicio rápido: clonar/abrir el proyecto; crear y activar venv; `pip install -r requirements.txt` y `python -m spacy download es_core_news_sm`; `streamlit run app.py`.
- Uso con Docker: `docker compose up --build` y puerto `8501`.
- Configuración: Gemini API Key en la barra lateral; ubicación del CSV del Compilado.
- Flujo de trabajo: subir archivo → revisar/segmentar → análisis → evaluación → retroalimentación (varios recursos) → descarga JSON/TOON.
- Estructura del repositorio y referencia a la documentación en `docs/`.
- Si quieres, el siguiente paso puede ser afinar el número de recursos por área (por ejemplo 2 por área y 6 total) o añadir una sección “Solución de problemas” en el README.


---

## 2026-03-18 - Dockerfile con UV

**Files**: `Dockerfile`  
**Objective**: Usar UV como instalador para acelerar el build en Docker y reducir peso.

### Descripción del Proceso

Quedó aplicado: el Dockerfile usa UV para instalar dependencias. Resumen de cambios:

Cambios realizados
UV como instalador

Se copia el binario desde la imagen oficial ghcr.io/astral-sh/uv:latest a /bin/uv (según la documentación de UV).
Variables de entorno

UV_COMPILE_BYTECODE=0: no genera .pyc, instalación más rápida y menos peso.
UV_LINK_MODE=copy: evita problemas con enlaces simbólicos en el contenedor.
Instalación de paquetes

RUN uv pip install --system --no-cache -r requirements.txt sustituye a pip install.
--system: instala en el Python del sistema (comportamiento esperado en Docker).
--no-cache: no guarda caché de descargas para mantener la imagen más pequeña.
Limpieza

Se eliminó curl de los paquetes del sistema porque ya no se usa el script de instalación de UV.
UV suele ser 10–100x más rápido que pip en instalaciones grandes (sobre todo con dependencias como torch), así que el build debería notarse mucho más rápido. Para probar:


docker compose build --no-cache

---

## 2026-03-18 - Métricas, UX y export (JSON/TOON)

**Files**: `analysis_engine.py`, `app.py`, `evaluator.py`, `file_processor.py`  
**Objective**: Afinar métricas y experiencia del asesor (dashboard, segmentación, resaltes, puntajes) y mejorar el export con sugerencias/recomendaciones.

### Descripción del Proceso

**1) Conteo de palabras (516 vs 475)**
- **Causa**: el relato por defecto era solo los primeros 1500 caracteres o la mitad del texto.
- **Cambio**: por defecto se usa todo el documento como relato, así el conteo coincide con Word. El texto se puede recortar después si se quiere.

**2) Dashboard de métricas**
- En el análisis se muestra:
  - Palabras del relato (con referencia 1 cuartilla ≈ 350, 2 ≈ 700).
  - Líneas y palabras de la reflexión (esperado 5–10 líneas).
  - Clases de palabras (% y aciertos/total).
  - Errores de ortografía/puntuación.
  - Duración del audio (y esperado 120–180 s).
- En Resultados de la evaluación cada criterio muestra el nivel y el puntaje (ej. "Experto" y "100 pts").

**3) Audio cuando el enlace está en el archivo**
- El enlace se sigue detectando y se rellena en el campo.
- Se añadió el mensaje: "Enlace detectado en el documento. Para transcribir el audio automáticamente, sube además el archivo de audio o video (MP3/MP4) en el selector de arriba."
- La transcripción solo puede hacerse con archivo subido (no con enlaces a Drive/YouTube sin descarga).

**4) Segmentación más práctica**
- "Detectar secciones automáticamente": localiza relato, reflexión y enlace (por frases como "diferencias que encontré", "oral y escrita", etc.) y rellena los cuadros.
- "Usar todo el documento como relato": pone todo el texto en el relato y vacía la reflexión.
- Los cuadros de texto se pueden seguir editando a mano.

**5) Vista previa con resaltes**
- En DOCX se genera un HTML con colores (verbos verde, sustantivos azul, adjetivos amarillo, adverbios rosa, artículos gris, preposiciones morado) y se usa en la vista previa (`meta["html_with_highlights"]`).

**6) Puntaje bajo cada criterio**
- En resultados se muestra, por criterio, el nivel y debajo el puntaje (ej. "Experto" y "100 pts"; Originalidad con "−X ded").

**7) JSON/TOON con sugerencias y recomendaciones**
- El export admite un `extra` con:
  - `filename`, `student_name`
  - `metrics` (`story_length`, `comparison_length`, `highlight_stats`, `orthography_errors`, `orthography_matches`)
  - `orthography_matches` (`message`, `contexto`, `sugerencia`)
  - `highlights_detail`, `suggestions`, `recommendations`
- Las recomendaciones de ortografía se muestran en un expander en el análisis y se incluyen en el JSON exportado.

**8) Nombre del alumno**
- Se infiere del nombre del archivo (Apellidos_Nombre_M02S1AI2 → "Nombre Apellidos").
- Hay un campo para corregirlo manualmente.
- Se usa en la retroalimentación y en el export.

**9) Evaluación manual completa**
- Formulario según la rúbrica:
  - 12 indicaciones actitudinales (checkboxes).
  - Nivel por criterio: Cognitivo, Actitudinal, Comunicativo, Pensamiento crítico (selectores).
  - Deducción por originalidad (0–100).
  - Observaciones.
- Al aplicar, se calcula el total y se rellena la evaluación para poder generar retroalimentación y exportar.

**10) Prompt de la retroalimentación**
- Nuevo expander "Ver prompt usado para la retroalimentación" que muestra:
  - System prompt (plantilla base, alineada con `m2_ai2_retroalimentacion.md`).
  - User prompt con los datos de la evaluación actual.
  - Referencia al doc: `docs/03_data_AI2/m2_ai2_retroalimentacion.md`.
- Archivos tocados: `app.py`, `file_processor.py` (detección de secciones, HTML con resaltes), `evaluator.py` (export con extra), `feedback_generator.py` (`get_prompt_preview`). Si quieres, puedo ajustar el formato del JSON de export para que coincida exactamente con el de la versión n8n (p. ej. `segments.historia`, `segments.enlace`).

---
## 2026-03-18 - Correcciones y mejora adicional (retro/heurísticas)

**Files**: `feedback_generator.py`, `analysis_engine.py`, `app.py`, `requirements.txt`
**Objective**: Ajustar el prompt de retro en prosa, mejorar el etiquetado de resaltados (caso “Nací”) y habilitar audio por liga dentro del documento.

### Descripción del Proceso

He hecho dos correcciones y una mejora relacionada:

1) feedback_generator.py prompt en prosa (sin numerales/viñetas)
Actualicé el system del generador para que la instrucción de estructura sea texto corrido (prosa) y ya no use la numeración tipo 1) ... 2) ... ni viñetas.

2) Resaltes: caso “Nací” (VERB esperado pero spaCy lo marca PROPN)
El problema era que tu app valida resaltados con spaCy, pero palabras conjugadas al inicio de oración (como “Nací”, con mayúscula) a veces las etiqueta como PROPN en lugar de VERB.

Copié/recuperé la idea de la versión antigua (processor_v4.py): cuando el esperado es VERB y spaCy detectó PROPN, ahora se aplica una heurística para verbos conjugados por terminación:

termina en í o é
o en aba / ía
Además, si spaCy puso PROPN, también intenta clasificar la misma palabra en minúsculas; si eso regresa AUX/VERB, se corrige.

Con esto, Nací (termina en í) debería marcar match=true como VERBO cuando esté en verde.

Archivos: analysis_engine.py (cambié pos_matches_category y la lógica de validate_highlights).

3) Audio por liga dentro del documento (descarga + transcripción automática)
Siguiendo la referencia de docs/04_old_version/audio_transcribe.py, añadí soporte para que la app intente descargar y transcribir cuando no se subió archivo de audio, pero sí hay audio_url dentro del documento.

analysis_engine.py: agregué transcribe_audio_url(audio_url)
app.py: en el botón Ejecutar Análisis, si no hay audio_path y existe audio_url, ahora llama transcribe_audio_url(audio_url).
requirements.txt: agregué gdown (para que Google Drive funcione mejor).
Siguiente paso (importante)
Como se cambió requirements.txt y el Dockerfile instala desde ese archivo, necesitas reconstruir la imagen/container con Docker para probar estos fixes.

---

## 2026-03-18 - Cambios aplicados (fallback, genai y ollama)

**Files**: `app.py`, `feedback_generator.py`, `requirements.txt`
**Objective**: Corregir fallos de import en contenedor, migrar a `google.genai` y agregar soporte de Ollama como alternativa a Gemini.

### Descripción del Proceso

**Resumen de los cambios aplicados**

**1) ImportError `detect_sections` (`app.py`)**
- Se añadió un fallback con `try/except`: si en el contenedor la versión de `file_processor` no define `detect_sections`, se importa solo `process_uploaded_file` y se define una `detect_sections` local que detecta la URL de audio por regex y divide relato/reflexión.
- Así la app arranca aunque la imagen Docker sea antigua. Si quieres usar la detección completa, reconstruye la imagen para que incluya el `file_processor.py` actual.

**2) Migración a `google.genai` y soporte Ollama (`feedback_generator.py`)**
- Nuevo SDK: si está instalado `google-genai`, se usa `from google import genai` y `genai.Client(api_key=...)` con `client.models.generate_content(..., config=types.GenerateContentConfig(system_instruction=...))`. Así desaparece el `FutureWarning` del paquete antiguo.
- Legacy: si no está el nuevo SDK, se sigue usando `google.generativeai` (sin cambiar la lógica de negocio).
- Ollama (si no hay API Key de Gemini o no está configurada):
  - Nueva función `_call_ollama(system_prompt, user_prompt, url=None, model="mistral")` que llama a `POST /api/chat` (como en `ollama_call_v4.py`).
  - URL por defecto: `OLLAMA_URL` o `http://localhost:11434`; modelo: `OLLAMA_MODEL` o `mistral`.
  - El mismo `system_instruction` y `user_content` que para Gemini se envían a Ollama para generar la retro.
- En la app se añadieron en la barra lateral:
  - `Ollama URL` (por defecto `http://localhost:11434` o el valor de `OLLAMA_URL`).
  - `Modelo Ollama` (por defecto `mistral` o `OLLAMA_MODEL`).
  - Esos valores se pasan a `FeedbackGenerator(..., ollama_url=..., ollama_model=...)`.

**3) Dependencias (`requirements.txt`)**
- Añadido `google-genai>=1.0.0` para usar el nuevo SDK por defecto.
- `google-generativeai` se mantiene como respaldo si no se instala el nuevo paquete.

**Uso rápido**
- Solo Gemini: configura “Gemini API Key” en la barra lateral (o `GEMINI_API_KEY`).
- Solo Ollama: deja la API Key vacía, indica `Ollama URL` (en Docker suele ser `http://host.docker.internal:11434`) y el modelo (ej. `mistral`). Asegúrate de tener Ollama en marcha y el modelo bajado (`ollama pull mistral`).
- Orden de uso: si hay API Key se usa Gemini (nuevo SDK o legacy); si no hay API Key pero hay Ollama URL, se usa Ollama; si no hay ninguno, se muestra el mensaje para configurar uno de los dos.
- Si quieres, el siguiente paso puede ser usar Ollama también para enriquecer fragmentos o métricas que se exportan en el JSON/TOON (por ejemplo con un modelo pequeño local para resumir o etiquetar secciones).

---

## 2026-03-18 - Actualización de README (Docker/Ollama)

**Files**: `README.md`
**Objective**: Documentar cómo levantar la app con Docker Compose y cómo usar Ollama dentro/fuera del contenedor; y aclarar por qué la terminal se “queda en un menú” cuando se ejecuta en primer plano.

### Descripción del Proceso

**Actualización aplicada en `README.md`**
- **Docker Compose**:
  - Recomendado: `docker compose up --build -d`
  - Logs: `docker compose logs -f evaluador_app`
  - Parar/borrar: `docker compose stop` y `docker compose down`
- **Ollama**:
  - `ollama serve`
  - `ollama pull mistral`
  - `ollama list`
- **Ollama en Docker (Windows)**: usar `Ollama URL: http://host.docker.internal:11434` y modelo `mistral` (por defecto).
- **Terminal “ocupada”**: es normal si corres `docker compose up --build` sin `-d` (queda en primer plano mostrando logs). Solución: usar `-d` y ver logs con `docker compose logs -f ...`.
- **Siguiente ajuste posible**: añadir al README un checklist explícito “sin Gemini (Gemini API Key vacío) => usar Ollama”.

---
## 2026-03-18 - Cuándo reconstruir Docker

**Files**: `Dockerfile`, `docker-compose.yml`, `requirements.txt`
**Objective**: Aclarar cuándo es necesario reconstruir la imagen del contenedor y cuándo solo basta reiniciar el servicio.

### Descripción del Proceso

**Uso de Docker (cuándo reconstruir)**
- Depende de qué cambiaste:
  - **Solo código Python** (ej. `app.py`, `feedback_generator.py`, `file_processor.py`): no necesitas reconstruir la imagen. Como tienes el volumen `.:/app` en `docker-compose.yml`, el contenedor suele ver los cambios al reiniciar Streamlit / recargar.
    - Basta con: `docker compose stop` y luego `docker compose up -d` (o simplemente `docker compose up -d`).
  - **Dependencias** (`requirements.txt`, p. ej. al agregar `google-genai>=1.0.0`): sí conviene reconstruir la imagen porque las librerías se instalan durante el build.
    - Lo correcto: `docker compose up --build -d`.
- Después revisas que ya inicia bien con: `docker compose logs -f evaluador_app`.
- Si quieres, dime el resultado de esos logs y te confirmo si ya quedó todo resuelto o si falta algún otro rebuild.

---
## 2026-03-18 - Fix de arranque en Docker (SyntaxError en regex)

**Files**: `analysis_engine.py`  
**Objective**: Corregir un `SyntaxError` que impedía iniciar Streamlit dentro del contenedor al parsear `content-disposition` en descargas (Dropbox/URLs directas).

### Descripción del Proceso
- Se corrigieron dos expresiones regulares en `analysis_engine.py` que estaban definidas con comillas simples y escapes conflictivos, provocando `SyntaxError` (mismatch de corchetes/paréntesis) al cargar el módulo.
- Se reemplazó el patrón por una versión equivalente en raw string con comillas dobles para extraer `filename` de `content-disposition`:
  - Patrón: `r"filename\*?=[\"']?([^\"';]+)"`

---
## 2026-03-18 - Verbos: corrección de POS reportado en resaltados

**Files**: `analysis_engine.py`  
**Objective**: Evitar que verbos conjugados al inicio de oración (ej. “Nací”) queden reportados como `PROPN` en el detalle de resaltados cuando el match es verdadero.

### Descripción del Proceso
- Se añadió `_lemma_looks_verb()` y se recupera `lemma` del token (si spaCy está disponible) para apoyar la heurística.
- En `validate_highlights`, cuando el esperado es `VERB` y spaCy detecta `PROPN`, se fuerza `detected="VERB"` si la palabra parece verbo (por lema o terminación), para que el reporte sea consistente (match true y detected VERB).

---
## 2026-03-18 - Audio por liga: error visible y exportado

**Files**: `analysis_engine.py`, `app.py`  
**Objective**: Mostrar por qué falla la transcripción por enlace (Drive/Dropbox/URL) y exportar el error en el JSON.

### Descripción del Proceso
- `transcribe_audio_url()` ahora retorna `(texto, duración, error)` en lugar de silenciar fallos.
- La UI muestra un warning cuando `transcription_error` existe.
- Se actualizó el mensaje informativo del enlace detectado para reflejar que se intentará descargar/transcribir (y que puede fallar si el enlace es privado).

---
## 2026-03-18 - Export: métricas/segmentos compatibles con versión antigua

**Files**: `app.py`  
**Objective**: Enriquecer el export JSON/TOON con estructura `metrics` y `segments` similar a la versión n8n v4.

### Descripción del Proceso
- Se añadieron `extra["segments"]` (historia, enlace, párrafo comparación, transcripción y highlights) y se enriqueció `extra["metrics"]` con `pages_approx`, `status`, `audio_found`, `ai_indicadores` y `orthography_matches` con claves `contexto/sugerencia`.

---
## 2026-03-18 - Audio: exportar motivo de fallo por permisos

**Files**: `analysis_engine.py`, `app.py`  
**Objective**: Si el enlace de Drive/Dropbox no tiene permisos, registrar en el JSON un motivo explícito (enlace privado/sin permisos) para que la retroalimentación indique cómo dar acceso.

### Descripción del Proceso
- Se normalizaron mensajes de error de descarga (Drive) para incluir una pista de permisos cuando aplica.
- Se añadió `extra["audio"]` en el export con `audio_url`, `download_ok` y `download_error` (texto listo para usar en retroalimentación).

---
## 2026-03-18 - Export: incluir fragmentos y frases sugeridas (retro)

**Files**: `app.py`, `evaluator.py`, `feedback_generator.py`  
**Objective**: Incluir en el JSON descargable los mismos `fragmentos_para_personalizar` y `frases_sugeridas_mapeo` que se usan en la ventana de retroalimentación.

### Descripción del Proceso
- Se calculan `fragmentos_para_personalizar` para export usando `build_fragmentos_retro(relato, reflexión, transcripción)`.
- Se reutiliza `build_eval_json_for_llm(...)` para obtener `frases_sugeridas_mapeo` (mapeo de métricas → frases).
- `Evaluator.export()` ahora pasa a JSON también: `segments`, `audio`, `fragmentos_para_personalizar` y `frases_sugeridas_mapeo` cuando vienen en `extra`.

---
## 2026-03-18 - Export: incluir recursos sugeridos (JSON/TOON)

**Files**: `app.py`, `evaluator.py`, `feedback_generator.py`  
**Objective**: Incluir en el export los recursos recomendados (por área) que se muestran en la retroalimentación, tanto en JSON como en TOON (formato compacto).

### Descripción del Proceso
- En `app.py` se agregan `recursos_sugeridos` al `extra` usando `FeedbackGenerator.get_suggested_materials(...)`.
- En `evaluator.py` se exporta `recursos_sugeridos` en JSON y se añade un token `recursos:` al TOON con una representación compacta `area=nombre@url;...`.

---
## 2026-03-18 - Rediseño de interfaz (layout profesional)

**Files**: `app.py`  
**Objective**: Reorganizar la UI en segmentos claros (preview/segmentación → análisis → evaluación → resultados → retro → manual → export/visor) y aplicar estilo profesional monocromático sin emojis.

### Descripción del Proceso
- Se añadió CSS monocromático (paneles, bordes, tipografía y radios) para un look profesional.
- Después de “Procesar Archivo”, se implementó un bloque de dos columnas: **vista previa** a la izquierda y **segmentación** a la derecha.
- Se creó un bloque de **Análisis automático** con columnas para métricas, fragmentos y detalles; el botón **Generar evaluación** se mueve al final del bloque.
- Resultados de evaluación se muestran en su propio bloque e incluyen el **nombre del alumno** en el encabezado.
- Retroalimentación con IA se organiza como bloque dedicado, con expander para ver prompt.
- Evaluación manual se convierte a bloque (no expander) y se mantiene compatible con export.
- Se agrega al final un bloque de **Export (JSON/TOON) y visor**, con text area con scroll para revisar el JSON generado.

---
## 2026-03-19 - Fix de compilación y fragmentos ampliados

**Files**: `app.py`  
**Objective**: Corregir error de indentación que impedía compilar la app y ampliar fragmentos exportados (relato/transcripción) para que el JSON incluya más contexto.

### Descripción del Proceso
- Se corrigió `IndentationError: unexpected indent` en la sección “Evaluación manual” (alineación de indentación del bloque).
- Se incrementó el tamaño de snippets en `build_fragmentos_retro(..., max_chars=...)` para análisis y export.
- Se añadieron fragmentos adicionales en el JSON exportado:
  - `historia_inicio`, `historia_medio`, `historia_fin`
  - `transcripcion_inicio`, `transcripcion_medio`, `transcripcion_fin`

---
## 2026-03-19 - UI: evaluación manual colapsable y contenedores consistentes

**Files**: `app.py`  
**Objective**: Evitar que la evaluación manual quede “cortada” o a media pantalla, reducir espacios vacíos por contenedores HTML mal cerrados y reintroducir iconografía monocromática (no emojis).

### Descripción del Proceso
- La sección “Evaluación manual” volvió a ser colapsable usando `st.expander(...)`.
- Se corrigió el cierre del contenedor de “Retroalimentación con IA” para que siempre se cierre aunque no exista `feedback`, evitando layout roto y espacios vacíos.
- Se agregaron íconos SVG monocromáticos en encabezados de secciones (Documento, Análisis, Manual, Resultados, IA, Export).

---
## 2026-03-19 - UI: preview más ancho, métricas en tabla y export colapsable

**Files**: `app.py`  
**Objective**: Mejorar legibilidad: vista previa más ancha y con borde/redondeo, métricas en tabla elegante, fragmentos sin “opacidad” de disabled y export en caja colapsable.

### Descripción del Proceso
- Se amplió la columna de vista previa (`st.columns([1.55, 0.85])`).
- Se añadió borde y esquinas redondeadas al iframe de vista previa (HTML component).
- Las métricas se renderizan como tabla (`st.dataframe`) en vez de lista de `st.metric`.
- Los fragmentos se muestran en cajas monoespaciadas sin `disabled` (sin apariencia de marca de agua).
- JSON/TOON + visor se movieron a un `st.expander("Abrir export y visor")`.

---
## 2026-03-19 - UI: snippets reales en análisis y botones de segmentación funcionales

**Files**: `app.py`  
**Objective**: Mostrar fragmentos breves (no texto completo) en Análisis automático, asegurar que “Detectar secciones / Usar todo como relato” sí modifiquen los campos visibles, y ajustar proporción de preview (menos ancho, más alto).

### Descripción del Proceso
- Se redujo `max_chars` de `build_fragmentos_retro` en análisis para que la sección muestre snippets más cortos y útiles.
- En “Fragmentos”, se cambió a cajas contenedoras dentro de expanders:
  - `Relato — snippet`
  - `Reflexión — snippet`
  - `Transcripción — snippet`
- Se corrigió el comportamiento de botones de segmentación actualizando directamente el estado de widgets (`seg_story`, `seg_refl`, `audio_url`) antes de `st.rerun()`.
- Se ajustó el layout de Documento a `st.columns([1.2, 1.0])` para reducir el ancho de preview.
- Se aumentó la altura de la vista previa/textarea a `680` para mejorar lectura longitudinal del contenido.

---
## 2026-03-19 - Ollama Docker, originalidad sin castigo por lectura y visor de prompt USER

**Files**: `feedback_generator.py`, `evaluator.py`, `app.py`  
**Objective**: Resolver fallo de Ollama cuando la app corre en contenedor, evitar deducción por similitud relato-transcripción (solo registrar), y mostrar JSON/prompt sin opacidad en el visor final.

### Descripción del Proceso
- Se reforzó `_call_ollama` con fallback de endpoints cuando `OLLAMA_URL` usa localhost:
  - URL configurada
  - `host.docker.internal`
  - `http://ollama:11434` (si existe servicio en red Docker)
- En `evaluator.py`, la deducción de originalidad ya no usa `similarity_suspicious`; la similitud alta entre relato y audio se registra en `similitud_relato_audio_alta` sin penalizar puntaje.
- En `feedback_generator.py`, el JSON para prompt incluye `similitud_relato_audio_alta` como contexto para el asesor sin activar castigo.
- En `app.py`, se añadió nota de ayuda en sidebar para Docker (`host.docker.internal`).
- En el visor de export:
  - JSON ahora se muestra en contenedor `mono-box` (sin efecto de opacidad por `disabled=True`).
  - Se agregó bloque **Prompt USER (para retroalimentación IA)**, visible siempre funcione o no Ollama.

---
## 2026-03-19 - Ajuste POS fino, robustez de modelo Ollama e iconos/visores

**Files**: `analysis_engine.py`, `feedback_generator.py`, `app.py`  
**Objective**: Corregir falsos positivos/negativos de clases de palabras en casos límite, endurecer entrada de modelo Ollama y mejorar visibilidad visual (iconos y contenedores JSON/prompt).

### Descripción del Proceso
- En `analysis_engine.py`:
  - Se añadió tolerancia pedagógica `ADJ` vs `ADV` para casos contextuales como “cerca”.
  - Se añadió heurística `_word_looks_like_noun(...)` y ajuste para evitar clasificar como `VERB` palabras esperadas como sustantivo (ej. “niñez”).
- En `feedback_generator.py`:
  - Se normaliza el nombre de modelo (`strip`, eliminación de `_` sobrante) y se completa con `:latest` cuando no viene etiqueta.
  - Esto evita fallos por entradas como `mistral_` o variantes sin tag.
- En `app.py`:
  - Se normaliza el valor de `ollama_model` desde sidebar antes de usarlo.
  - Se reforzó la visibilidad de iconos SVG (`.section-title .ico`) para que no se pierdan en el tema.
  - Los visores de JSON y Prompt usan fondo gris claro con texto oscuro nítido (sin opacidad visual).

---
## 2026-03-19 - Ollama URL por defecto a host.docker.internal

**Files**: `app.py`, `feedback_generator.py`  
**Objective**: Usar por defecto la ruta funcional de Ollama en entorno Docker del proyecto.

### Descripción del Proceso
- Se cambió el valor por defecto de `Ollama URL (opcional)` en sidebar a `http://host.docker.internal:11434`.
- Se ajustó el texto de ayuda contextual para recomendar explícitamente esa ruta cuando se detecte `localhost`.
- Se actualizó el mensaje de fallback en `feedback_generator.py` para mostrar el mismo ejemplo de URL.

---
## 2026-03-19 - UI: contraste de títulos e íconos

**Files**: `app.py`  
**Objective**: Corregir baja visibilidad de encabezados de segmentos e íconos en el tema actual.

### Descripción del Proceso
- Se ajustó la paleta CSS base de paneles/contornos a tonos claros con contraste consistente.
- Se forzó color oscuro y mayor peso en `.section-title` para evitar títulos “en blanco” sobre fondos claros.
- Se forzó color oscuro en `.ico` y `.section-title .ico` para que los SVG monocromáticos se vean nítidos.

---
## 2026-03-19 - UI: reemplazar barra superior por línea bajo título

**Files**: `app.py`  
**Objective**: Quitar la barra gruesa que aparece arriba de encabezados y usar una línea fina justo debajo del título, sin espacio.

### Descripción del Proceso
- Se redefinió `.section-title` para incluir `border-bottom: 1px solid ...` con `margin-bottom: 0`, dejando la línea pegada al texto.
- Se neutralizó `.section-box` (sin fondo/borde/padding/margen) para evitar la barra vacía que Streamlit renderizaba al abrir/cerrar contenedores HTML en bloques separados.

---
## 2026-03-19 - Ajustes finales UI/JSON/POS y política de originalidad

**Files**: `app.py`, `analysis_engine.py`, `evaluator.py`  
**Objective**: Afinar espaciados visuales, eliminar TOON, mejorar visor JSON, corregir falsos negativos de clases de palabras y evitar penalización por similitud relato-transcripción.

### Descripción del Proceso
- UI:
  - Se agregó margen después de la línea bajo título (`.section-title`) para separar visualmente encabezado y contenido.
  - Se añadió margen inferior a `.mono-box` para evitar que el borde interno quede pegado al borde del expander con scroll.
- Export:
  - Se eliminó la descarga TOON en la interfaz, quedando solo descarga JSON.
  - El visor JSON ahora usa `st.code(..., language="json")` para mostrar estructura con sangrías y saltos.
- POS / resaltados:
  - Se normalizó `expected_category` (trim/uppercase + mapeo español→POS) para evitar desajustes por formato.
  - Se reforzó corrección para sustantivos (ej. “niñez”) y se normaliza visualmente `ADJ` cuando spaCy reporta `ADV` en casos aceptados (ej. “cerca”).
- Originalidad:
  - La deducción ahora solo aplica si hay bandera explícita `plagio_externo=True`.
  - Similitud alta relato-transcripción queda solo como registro contextual, sin castigo de puntaje.

---
## 2026-03-19 - Resaltados (highlights) desde PDF, PPTX, imagen y video

**Files**: `file_processor.py`, `requirements.txt`  
**Objective**: Obtener palabras resaltadas y su categoría esperada en formatos distintos a Word: PPTX (color de fuente), PDF (color de span y anotaciones), imagen (OCR + color por bbox) y video (frames + pipeline de imagen).

### Descripción del Proceso
- **Mapeo de color común**: Se añadió `rgb_to_category` (distancia a anclas RGB por categoría), `color_to_category` (hex o RGB → categoría + confidence) y `normalize_highlight` para un formato unificado de highlight (`word`, `expected_category`, `source`, `confidence`, `color_hex`). DOCX sigue usando `hex_to_category` y ahora también devuelve entradas normalizadas.
- **PPTX**: Se extrae el color de fuente de cada run (`font.color.rgb`). Se mapea a categoría y se construye lista de highlights y HTML con spans coloreados. Retorno: `(text, html, highlights)`.
- **PDF**: Dos rutas. (A) Con PyMuPDF: `get_text("dict")` para obtener spans con color, conversión a RGB y mapeo a categoría. (B) Anotaciones tipo highlight: se obtiene el texto en el rect de la anotación y el color de la anotación; si no hay mapeo, se usa categoría genérica. Si PyMuPDF no está instalado, solo se extrae texto sin highlights. Retorno: `(text, html, highlights)`.
- **Imagen**: Se usa `pytesseract.image_to_data` para obtener bbox por palabra. Para cada palabra se muestrea el color dominante en la región (bbox expandida, excluyendo blanco) y se mapea a categoría. Retorno: `(text, html, highlights)`.
- **Video**: Se extraen frames cada N segundos (`extract_highlights_from_video`), se ejecuta el pipeline de imagen (OCR + color por bbox) en cada frame y se fusionan highlights por `(word, category)` quedándose la mayor confidence.
- **Audio**: Sin cambios en contenido; se establece `meta["highlight_fallback_reason"]` para indicar que no hay detección de color.
- **Router**: `process_uploaded_file` ahora recibe y devuelve `highlights` en PDF, PPTX, imagen y video, y rellena `meta["highlight_fallback_reason"]` cuando no se detectan resaltados en esos formatos.
- **Dependencia**: Se añadió `pymupdf` en `requirements.txt` para la ruta PDF con color.

---
## 2026-03-19 - Robustez highlights: fondo real, no color de texto

**Files**: `file_processor.py`, `app.py`  
**Objective**: Corregir la detección de resaltados para que solo use color de **fondo/sombreado** (highlight real, rectángulos dibujados, anotaciones), **nunca** color del texto (foreground). Filtrar highlights al segmento "relato". Arreglar wrap del visor JSON.

### Cambios en `file_processor.py`
- **PDF** — Se reescribió `_extract_highlights_from_pdf_fitz` → `_extract_highlights_from_pdf_drawings`:
  - Ya NO se lee `span["color"]` (foreground). Se eliminó toda la lógica de color de texto en spans.
  - Ahora se iteran `page.get_drawings()` buscando rectángulos con `fill` (color de relleno). Se descartan colores neutros (blanco, negro, grises) vía `_is_neutral_color`.
  - Cada rectángulo coloreado se cruza con las palabras de la página (`page.get_text("words")`); si el rect cubre ≥50% del ancho y ≥30% de la altura de la palabra, se asigna la categoría del color.
  - Se mantiene `_extract_highlights_from_pdf_annotations` como ruta B (anotaciones tipo 8 = highlight markup).
- **PPTX** — Se reescribió `_pptx_run_rgb` → `_pptx_run_highlight_rgb`:
  - Ya NO se lee `run.font.color.rgb` (color de fuente). Se busca el XML `<a:highlight><a:srgbClr val="..."/>` dentro de `<a:rPr>`, que es el fondo del run.
  - Se descartan colores neutros con `_is_neutral_color`.
- **Imagen** — Se reescribió `_image_bbox_dominant_color` → `_image_bbox_background_color`:
  - Se muestrean píxeles del borde exterior del bbox (margen 3px). Se excluyen píxeles muy oscuros (tinta del texto, brightness < 80) y blancos puros (> 245 por canal).
  - Si el promedio resultante es neutro, retorna `None`.
- **Video** — Sin cambios directos; hereda la mejora de imagen vía `_image_to_highlights_only` → `extract_text_from_image`.
- **Audio** — Sin cambios; no hay color que detectar.
- **Utilidad** — Se añadió `_is_neutral_color(r, g, b)` que identifica blancos, negros y grises (tanto claros como oscuros).

### Cambios en `app.py`
- **Filtrado por segmento "relato"**: Antes de llamar a `validate_highlights`, se filtran los highlights dejando solo los cuyas palabras existen en el texto del relato segmentado. Evita evaluar highlights de secciones como reflexión, enlaces o notas al pie.
- **Visor JSON**: Se reemplazó `st.code(json_data)` por un `<div class="mono-box"><pre>` con `white-space: pre-wrap; overflow-wrap: anywhere; word-break: break-word;` para garantizar wrap visible en cualquier ancho de ventana.
- **Caption actualizado**: La leyenda del Ejercicio 2 ahora dice "se detectan por sombreado/fondo de color en Word, PDF, PPTX o imagen".

---
## 2026-05-18 - Descarga de audio OneDrive (token Badger)

**Files**: `analysis_engine.py`, `scratch/test_onedrive.py`, `README.md`  
**Objective**: Restaurar descarga de audio desde enlaces OneDrive/1drv.ms; la API `api.onedrive.com/v1.0/shares/.../content` ya no funciona sin autenticación (401).

### Cambios
- Se eliminó `_onedrive_direct_url` (API antigua sin auth).
- Nuevo flujo Badger (2025): POST token en `api-badgerp.svc.ms`, luego POST a `my.microsoftpersonalcontent.com/_api/v2.0/shares/u!{encoded}/driveitem` con header `Authorization: Badger {token}` y `Prefer: autoredeem`; se obtiene `@content.downloadUrl`.
- Codificación de URL según Microsoft: `base64` estándar → quitar `=` → reemplazar `/` y `+` → prefijo `u!` en la ruta.
- Resolución de enlaces cortos `1drv.ms` con GET (redirect).
- Fallbacks: SharePoint `?download=1`, URLs legacy (`redir`, `download`, `download.aspx`).
- Detección de redirect a `login.live.com` con mensaje claro de permisos.
- `scratch/test_onedrive.py` y sección en `README.md` para probar enlaces públicos (preferir `1drv.ms`).