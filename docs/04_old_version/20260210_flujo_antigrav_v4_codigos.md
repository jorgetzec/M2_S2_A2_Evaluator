# Flujo de Evaluación n8n – v4 (Modular: Python + Ollama + ChatGPT)

Versión v4 que **modulariza** el análisis: Python hace todas las métricas cuantitativas, Ollama (Mistral) realiza 3 análisis cualitativos puntuales, y ChatGPT genera la retroalimentación final.

**Cambios clave vs v3:**
- **Métricas flexibles:** tolerancias más amplias para no penalizar errores menores.
- **Flujo modular:** cada análisis cualitativo es un nodo Ollama separado y enfocado.
- **Reporte mejorado:** formato con tablas de evaluación por criterio (Cognitivo, Actitudinal, Comunicativo, Pensamiento Crítico, Originalidad).
- **3 documentos de salida:** Reporte completo, Evaluación (para ChatGPT) y Retroalimentación.

Requisitos: n8n en Docker, Ollama con Mistral en el host, API key OpenAI (para ChatGPT).

---

## Esquema del flujo v4

```
  Secuencia principal (vertical)

  [1] Schedule Trigger
       │
       ▼
  [2] EC – v4 Listar DOCX
       │
       ▼
  [3] Code – v4 Split Files
       │
       ▼
  [4] EC – v4 Processor Python
       │
       ▼
  [5] Code – v4 Parse Métricas + Prompt Relato
       │
       ▼
  [6] EC – v4 Ollama Análisis Relato (Python)
       │
       ▼
  [7] Code – v4 Extract Relato + Prompt Audio
       │
       ▼
  [8] EC – v4 Ollama Análisis Audio (Python)
       │
       ▼
  [9] Code – v4 Extract Audio + Prompt Párrafo
       │
       ▼
  [10] EC – v4 Ollama Análisis Párrafo (Python)
       │
       ▼
  [11] Code – v4 Build Report + Evaluación
       │
       ├──────────────────┬──────────────────┬──────────────────┐
       │                  │                  │                  │
       ▼                  ▼                  ▼                  ▼
  [12] EC             [13] EC           [14] Code          (rama ChatGPT)
  Guardar reporte     Guardar eval      Prep ChatGPT
       │                                    │
       ▼                                    ▼
  [18] EC                              [15] HTTP ChatGPT
  Copiar a procesados                       │
                                       [15b] Merge (14+15)
                                            │
                                            ▼
                                       [16] Code Extract ChatGPT
                                            │
                                            ▼
                                       [17] EC Guardar Retro
                                            │
                                            ▼
                                       [19] Code Concatenar Todo
                                            │
                                            ▼
                                       [20] EC Guardar Todo
```

**Conexiones en n8n:**
- **1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11** (secuencia principal).
- **11 → 12 → 18** (guardar reporte → copiar a procesados).
- **11 → 13** (guardar evaluación).
- **11 → 14** (prep ChatGPT). **14 → 15** (HTTP ChatGPT).
- **14 → 15b** (Merge input 1), **15 → 15b** (Merge input 2).
- **15b → 16** (extraer respuesta ChatGPT).
- **16 → 17 → 19 → 20** (extraer respuesta ChatGPT → guardar retroalimentación → concatenar reporte+eval+retro → guardar archivo completo).

---

## Listado de nodos

| # | Tipo | Nombre sugerido | Descripción |
|---|------|-----------------|-------------|
| 1 | Schedule | v4 Programación | Disparador |
| 2 | Execute Command | v4 Listar DOCX | Lista .docx pendientes |
| 3 | Code | v4 Split Files | Un ítem por archivo |
| 4 | Execute Command | v4 Processor Python | Ejecuta processor_v4.py |
| 5 | Code | v4 Parse Métricas | Parsea JSON, prepara prompt relato |
| 6 | Execute Command | v4 Ollama Relato | Llama ollama_call_v4.py – análisis relato |
| 7 | Code | v4 Extract Relato | Extrae respuesta, prepara prompt audio |
| 8 | Execute Command | v4 Ollama Audio | Llama ollama_call_v4.py – análisis audio |
| 9 | Code | v4 Extract Audio | Extrae respuesta, prepara prompt párrafo |
| 10 | Execute Command | v4 Ollama Párrafo | Llama ollama_call_v4.py – análisis párrafo |
| 11 | Code | v4 Build Report Eval | Construye reporte + evaluación |
| 12 | Execute Command | v4 Guardar Reporte | Escribe Reporte_XXX.md |
| 13 | Execute Command | v4 Guardar Evaluación | Escribe Evaluacion_XXX.md |
| 14 | Code | v4 Prep ChatGPT | Construye prompt con ejemplo (few-shot) |
| 15 | HTTP Request | v4 ChatGPT | POST a OpenAI |
| 15b | Merge | v4 Merge ChatGPT | Combina 14 + 15 |
| 16 | Code | v4 Extract ChatGPT | Extrae texto de la respuesta |
| 17 | Execute Command | v4 Guardar Retro | Escribe Retroalimentacion_XXX.md |
| 18 | Execute Command | v4 Copiar Procesados | Mueve DOCX a procesados |
| 19 | Code | v4 Concatenar Todo | Une Reporte + Eval + Retro |
| 20 | Execute Command | v4 Guardar Todo | Escribe Completo_XXX.md |

---

## Métricas flexibles v4 (vs v3 estricto)

| Métrica | v3 (estricto) | v4 (flexible) |
|---------|---------------|---------------|
| Extensión relato | 350-1000 pal → Experto | **280-1100** pal → Experto |
| Clases de palabras | ≥90% → Experto | **≥85%** → Experto |
| Duración audio | 120-180 s → Experto | **90-240 s** → Experto |
| Párrafo extensión | 5-10 líneas → Experto | **3-14** líneas → Experto |
| Actitudinal | 12/12 → Experto | **10/12** → Experto |
| Ortografía | 0 errores → Experto | **0-2** errores → Experto |
| Cognitivo global | mín(subcriterios) | **3/4 Experto + 1 Aceptable → Experto** |

---

## Nodo 1 – Schedule (v4 Programación)

- **Tipo:** Schedule Trigger
- **Regla:** Cada 1 minuto (o manual para pruebas).

---

## Nodo 2 – v4 Listar DOCX

- **Tipo:** Execute Command
- **Comando:**

```bash
# Listar archivos DOCX
sh -c 'mkdir -p /home/node/entradas/procesados; for f in /home/node/entradas/*.docx; do [ -f "$f" ] && [ ! -f "/home/node/entradas/procesados/$(basename "$f")" ] && echo "$f"; done'

# Listar archivos DOCX y PDF no procesados
sh -c 'mkdir -p /home/node/entradas/procesados; for f in /home/node/entradas/*; do if [ -f "$f" ]; then ext="${f##*.}"; if [ "$ext" = "docx" ] || [ "$ext" = "pdf" ]; then if [ ! -f "/home/node/entradas/procesados/$(basename "$f")" ]; then echo "$f"; fi; fi; fi; done; exit 0'
```

---

## Nodo 3 – v4 Split Files (Code)

```javascript
const rawOutput = $json.stdout;
if (!rawOutput || rawOutput.trim() === "") return [];
return rawOutput.trim().split('\n').filter(line => line.trim()).map(line => ({
  json: { filePath: line.trim() }
}));
```

---

## Nodo 4 – v4 Processor Python

- **Tipo:** Execute Command
- **Comando:**

```bash
python3 /home/node/scripts/processor_v4.py "{{ $json.filePath }}"
```

- **Nota:** Usa processor_v4.py (no processor.py). La salida es JSON en stdout con métricas flexibles y datos para Ollama. **Soporta archivos .docx y .pdf** (los PDF se convierten a DOCX internamente).

---

## Nodo 5 – v4 Parse Métricas + Prep Ollama Relato (Code)

Parsea la salida del processor, calcula métricas base y prepara el prompt para el primer análisis Ollama. **Los prompts se codifican en base64** para que Execute Command los pase a Python sin problemas de escape.

```javascript
let rawData = $json;
let data = {};
try {
  data = rawData.stdout ? JSON.parse(rawData.stdout) : rawData;
} catch (e) {
  return [{ json: { error: "Error parseando JSON", details: String(e) } }];
}

const filename = (data.filename || "Archivo").replace(/\.docx$/i, "").trim();
const ollama = data.ollama_inputs || {};

// Construir prompt para Análisis del Relato
const historia = ollama.historia_snippet || "";
const userPrompt = ollama.tiene_historia
  ? "Analiza este relato de vida de un estudiante:\n\n" + historia + '\n\nResponde SOLO con un JSON exacto:\n{"claridad": "Claro/Poco claro/Confuso", "coherencia": "Coherente/Parcialmente/Incoherente", "precision": "Precisa/Imprecisa", "extracto_mejorable": "[frase que se podría redactar mejor]", "punto_fuerte": "[frase o fragmento breve que destaque por su redacción o emotividad]"}'
  : 'No hay texto del relato. Responde: {"claridad":"No evaluado","coherencia":"No evaluado","precision":"No evaluado","extracto_mejorable":"","punto_fuerte":""}';

const promptJson = JSON.stringify({
  system: "Evalúa la organización de un texto académico. Responde SOLO con un JSON válido, sin texto adicional.",
  user: userPrompt,
  model: "mistral"
});
const ollamaRelatoB64 = Buffer.from(promptJson).toString('base64');

return [{ json: { filename, data, ollamaRelatoB64 } }];
```

**Version anterior**
```javascript
let rawData = $json;
let data = {};
try {
  data = rawData.stdout ? JSON.parse(rawData.stdout) : rawData;
} catch (e) {
  return [{ json: { error: "Error parseando JSON", details: String(e) } }];
}

const filename = (data.filename || "Archivo").replace(/\.docx$/i, "").trim();
const ollama = data.ollama_inputs || {};

// Construir prompt para Análisis del Relato
const historia = ollama.historia_snippet || "";
const userPrompt = ollama.tiene_historia
  ? "Analiza la organización de este relato de un estudiante de preparatoria:\n\n" + historia + '\n\nResponde SOLO con un JSON exacto (sin texto antes ni después):\n{"claridad": "Claro" o "Poco claro" o "Confuso", "coherencia": "Coherente" o "Parcialmente coherente" o "Incoherente", "precision": "Precisa" o "Imprecisa", "extracto_claridad": "[frase breve del texto]", "extracto_coherencia": "[frase breve]", "extracto_precision": "[frase breve]"}'
  : 'No hay texto del relato. Responde: {"claridad":"No evaluado","coherencia":"No evaluado","precision":"No evaluado","extracto_claridad":"","extracto_coherencia":"","extracto_precision":""}';

const promptJson = JSON.stringify({
  system: "Evalúa la organización de un texto académico. Responde SOLO con un JSON válido, sin texto adicional.",
  user: userPrompt,
  model: "mistral"
});
const ollamaRelatoB64 = Buffer.from(promptJson).toString('base64');

return [{ json: { filename, data, ollamaRelatoB64 } }];
```

---

## Nodo 6 – v4 Ollama Análisis Relato (Execute Command)

- **Tipo:** Execute Command
- **Comando:**

```bash
echo '{{ $json.ollamaRelatoB64 }}' | base64 -d | python3 /home/node/scripts/ollama_call_v4.py
```

> **¿Por qué Execute Command y no HTTP Request?** El HTTP Request de n8n tiene problemas de codificación con textos largos del estudiante (comillas, saltos de línea, caracteres especiales rompen el JSON). Python maneja todo esto nativamente sin errores. El script `ollama_call_v4.py` hace la llamada HTTP a Ollama desde dentro del contenedor, que ya probamos que funciona perfectamente.

---

## Nodo 7 – v4 Extract Relato + Prep Audio (Code)

Extrae la respuesta de Ollama sobre el relato y prepara el prompt para el audio.

```javascript
// Función reutilizable para parsear respuesta de Ollama
function parseOllamaJSON(rawStdout) {
  let data = {};
  try {
    data = typeof rawStdout === "string" ? JSON.parse(rawStdout) : rawStdout;
  } catch(e) { return null; }
  // Extraer el texto del message.content
  let text = "";
  if (data.message && data.message.content) text = data.message.content;
  else if (data.response) text = data.response;
  else if (data.error) return null;
  if (!text) return null;
  text = text.trim();
  // Parsear el JSON que Ollama genera dentro del texto
  try { return JSON.parse(text); } catch(e) {}
  const match = text.match(/\{[\s\S]*?\}/);
  if (match) { try { return JSON.parse(match[0]); } catch(e) {} }
  return null;
}

const prevData = $('n5_Parse Métricas').item.json;
const ollamaRaw = $json.stdout || JSON.stringify($json);
const data = prevData.data;
const filename = prevData.filename;
const ollama = data.ollama_inputs || {};

// Extraer análisis del relato
const analisis_relato = parseOllamaJSON(ollamaRaw) || {
  claridad: "No evaluado", coherencia: "No evaluado", precision: "No evaluado",
  extracto_claridad: "", extracto_coherencia: "", extracto_precision: ""
};

// Preparar prompt base64 para Ollama: Análisis del Audio
const transcripcion = ollama.transcripcion_snippet || "";
const userPrompt = ollama.tiene_transcripcion
  ? "Esta es la transcripción del audio de un estudiante:\n\n" + transcripcion + '\n\nEvalúa el discurso oral. Responde SOLO con un JSON exacto:\n{"calidad_tecnica": "Alta/Media/Baja", "fluidez": "Fluido/Comprensible/Poco fluido", "comprensibilidad": "Alta/Media/Baja", "lee_o_narra": "Lee/Narra", "punto_fuerte_oral": "[frase breve del audio que destaque]", "observaciones": "[breve comentario]"}'
  : 'No hay transcripción. Responde: {"calidad_tecnica":"No evaluado","fluidez":"No evaluado","comprensibilidad":"No evaluado","lee_o_narra":"No determinado","punto_fuerte_oral":"","observaciones":"Sin audio"}';

const promptJson = JSON.stringify({
  system: "Evalúa el discurso oral de un estudiante. Responde SOLO con un JSON válido.",
  user: userPrompt,
  model: "mistral"
});
const ollamaAudioB64 = Buffer.from(promptJson).toString('base64');

return [{ json: { filename, data, analisis_relato, ollamaAudioB64 } }];
```

**Version anterior**

```javascript
// Función reutilizable para parsear respuesta de Ollama
function parseOllamaJSON(rawStdout) {
  let data = {};
  try {
    data = typeof rawStdout === "string" ? JSON.parse(rawStdout) : rawStdout;
  } catch(e) { return null; }
  // Extraer el texto del message.content
  let text = "";
  if (data.message && data.message.content) text = data.message.content;
  else if (data.response) text = data.response;
  else if (data.error) return null;
  if (!text) return null;
  text = text.trim();
  // Parsear el JSON que Ollama genera dentro del texto
  try { return JSON.parse(text); } catch(e) {}
  const match = text.match(/\{[\s\S]*?\}/);
  if (match) { try { return JSON.parse(match[0]); } catch(e) {} }
  return null;
}

const prevData = $('n5_Parse Métricas').item.json;
const ollamaRaw = $json.stdout || JSON.stringify($json);
const data = prevData.data;
const filename = prevData.filename;
const ollama = data.ollama_inputs || {};

// Extraer análisis del relato
const analisis_relato = parseOllamaJSON(ollamaRaw) || {
  claridad: "No evaluado", coherencia: "No evaluado", precision: "No evaluado",
  extracto_claridad: "", extracto_coherencia: "", extracto_precision: ""
};

// Preparar prompt base64 para Ollama: Análisis del Audio
const transcripcion = ollama.transcripcion_snippet || "";
const userPrompt = ollama.tiene_transcripcion
  ? "Esta es la transcripción del audio de un estudiante:\n\n" + transcripcion + '\n\nEvalúa el discurso oral. Responde SOLO con un JSON exacto:\n{"calidad_tecnica": "Alta/Media/Baja", "fluidez": "Fluido/Comprensible/Poco fluido", "comprensibilidad": "Alta/Media/Baja", "lee_o_narra": "Lee/Narra", "punto_fuerte_oral": "[frase breve del audio que destaque]", "observaciones": "[breve comentario]"}'
  : 'No hay transcripción. Responde: {"calidad_tecnica":"No evaluado","fluidez":"No evaluado","comprensibilidad":"No evaluado","lee_o_narra":"No determinado","punto_fuerte_oral":"","observaciones":"Sin audio"}';

const promptJson = JSON.stringify({
  system: "Evalúa el discurso oral de un estudiante. Responde SOLO con un JSON válido.",
  user: userPrompt,
  model: "mistral"
});
const ollamaAudioB64 = Buffer.from(promptJson).toString('base64');

return [{ json: { filename, data, analisis_relato, ollamaAudioB64 } }];
```


**Nota:** Ajustar `$('v4 Parse Métricas')` al nombre exacto del nodo 5 en tu flujo.

---

## Nodo 8 – v4 Ollama Análisis Audio (Execute Command)

- **Tipo:** Execute Command
- **Comando:**

```bash
echo '{{ $json.ollamaAudioB64 }}' | base64 -d | python3 /home/node/scripts/ollama_call_v4.py
```

---

## Nodo 9 – v4 Extract Audio + Prep Párrafo (Code)

Extrae análisis del audio y prepara el prompt para el párrafo de reflexión.

```javascript
function parseOllamaJSON(rawStdout) {
  let data = {};
  try {
    data = typeof rawStdout === "string" ? JSON.parse(rawStdout) : rawStdout;
  } catch(e) { return null; }
  let text = "";
  if (data.message && data.message.content) text = data.message.content;
  else if (data.response) text = data.response;
  if (!text) return null;
  text = text.trim();
  try { return JSON.parse(text); } catch(e) {}
  const match = text.match(/\{[\s\S]*?\}/);
  if (match) { try { return JSON.parse(match[0]); } catch(e) {} }
  return null;
}

const prevData = $('n7_ Extract Relato + Prep Audio').item.json;
const ollamaRaw = $json.stdout || JSON.stringify($json);
const data = prevData.data;
const filename = prevData.filename;
const analisis_relato = prevData.analisis_relato;
const ollama = data.ollama_inputs || {};

// Extraer análisis del audio
const analisis_audio = parseOllamaJSON(ollamaRaw) || {
  calidad_tecnica: "No evaluado", fluidez: "No evaluado",
  comprensibilidad: "No evaluado", lee_o_narra: "No determinado", observaciones: "Sin evaluación"
};

// Preparar prompt base64 para Ollama: Análisis del Párrafo
const parrafo = ollama.parrafo_snippet || "";
const userPrompt = ollama.tiene_parrafo
  ? "Este es el párrafo donde un estudiante analiza diferencias entre comunicación oral y escrita:\n\n" + parrafo + '\n\n¿Identifica correctamente diferencias? Responde SOLO con un JSON exacto:\n{"identifica_diferencias": true o false, "nivel_identificacion": "Claro" o "Con dificultad" o "Con errores" o "No identifica", "coherencia_analisis": "Coherente" o "Parcialmente coherente" o "Incoherente", "extractos": "[fragmentos relevantes]"}'
  : 'No hay párrafo. Responde: {"identifica_diferencias":false,"nivel_identificacion":"No identifica","coherencia_analisis":"No evaluado","extractos":""}';

const promptJson = JSON.stringify({
  system: "Evalúa un párrafo académico sobre diferencias entre comunicación oral y escrita. Responde SOLO con un JSON válido.",
  user: userPrompt,
  model: "mistral"
});
const ollamaParrafoB64 = Buffer.from(promptJson).toString('base64');

return [{ json: { filename, data, analisis_relato, analisis_audio, ollamaParrafoB64 } }];
```

**Anterior version**
```javascript
function parseOllamaJSON(rawStdout) {
  let data = {};
  try {
    data = typeof rawStdout === "string" ? JSON.parse(rawStdout) : rawStdout;
  } catch(e) { return null; }
  let text = "";
  if (data.message && data.message.content) text = data.message.content;
  else if (data.response) text = data.response;
  if (!text) return null;
  text = text.trim();
  try { return JSON.parse(text); } catch(e) {}
  const match = text.match(/\{[\s\S]*?\}/);
  if (match) { try { return JSON.parse(match[0]); } catch(e) {} }
  return null;
}

const prevData = $('n7_ Extract Relato + Prep Audio').item.json;
const ollamaRaw = $json.stdout || JSON.stringify($json);
const data = prevData.data;
const filename = prevData.filename;
const analisis_relato = prevData.analisis_relato;
const ollama = data.ollama_inputs || {};

// Extraer análisis del audio
const analisis_audio = parseOllamaJSON(ollamaRaw) || {
  calidad_tecnica: "No evaluado", fluidez: "No evaluado",
  comprensibilidad: "No evaluado", lee_o_narra: "No determinado", observaciones: "Sin evaluación"
};

// Preparar prompt base64 para Ollama: Análisis del Párrafo
const parrafo = ollama.parrafo_snippet || "";
const userPrompt = ollama.tiene_parrafo
  ? "Este es el párrafo donde un estudiante analiza diferencias entre comunicación oral y escrita:\n\n" + parrafo + '\n\n¿Identifica correctamente diferencias? Responde SOLO con un JSON exacto:\n{"identifica_diferencias": true o false, "nivel_identificacion": "Claro" o "Con dificultad" o "Con errores" o "No identifica", "coherencia_analisis": "Coherente" o "Parcialmente coherente" o "Incoherente", "extractos": "[fragmentos relevantes]"}'
  : 'No hay párrafo. Responde: {"identifica_diferencias":false,"nivel_identificacion":"No identifica","coherencia_analisis":"No evaluado","extractos":""}';

const promptJson = JSON.stringify({
  system: "Evalúa un párrafo académico sobre diferencias entre comunicación oral y escrita. Responde SOLO con un JSON válido.",
  user: userPrompt,
  model: "mistral"
});
const ollamaParrafoB64 = Buffer.from(promptJson).toString('base64');

return [{ json: { filename, data, analisis_relato, analisis_audio, ollamaParrafoB64 } }];
```

**Nota:** Ajustar `$('v4 Extract Relato')` al nombre exacto del nodo 7.

---

## Nodo 10 – v4 Ollama Análisis Párrafo (Execute Command)

- **Tipo:** Execute Command
- **Comando:**

```bash
echo '{{ $json.ollamaParrafoB64 }}' | base64 -d | python3 /home/node/scripts/ollama_call_v4.py
```

---

## Nodo 11 – v4 Build Report + Evaluación (Code)

Este es el nodo central: extrae el último análisis de Ollama, integra todo y construye el reporte completo + documento de evaluación para ChatGPT.

```javascript
// ===== PARSING DE OLLAMA (Execute Command → stdout) =====
function parseOllamaJSON(rawStdout) {
  let data = {};
  try {
    data = typeof rawStdout === "string" ? JSON.parse(rawStdout) : rawStdout;
  } catch(e) { return null; }
  let text = "";
  if (data.message && data.message.content) text = data.message.content;
  else if (data.response) text = data.response;
  if (!text) return null;
  text = text.trim();
  try { return JSON.parse(text); } catch(e) {}
  const match = text.match(/\{[\s\S]*?\}/);
  if (match) { try { return JSON.parse(match[0]); } catch(e) {} }
  return null;
}

// ===== DATOS ACUMULADOS =====
const prevData = $('n9_Extract Audio').item.json;
const ollamaRaw = $json.stdout || JSON.stringify($json);
const data = prevData.data;
const filename = prevData.filename;
const analisis_relato = prevData.analisis_relato || {};
const analisis_audio = prevData.analisis_audio || {};

// Extraer análisis del párrafo (desde stdout de Execute Command)
const analisis_parrafo = parseOllamaJSON(ollamaRaw) || {
  identifica_diferencias: false, nivel_identificacion: "No evaluado",
  coherencia_analisis: "No evaluado", extractos: ""
};

// ===== MAPEOS DE NIVEL =====
function mapToLevel(val, mapping) {
  if (!val || val === "No evaluado") return "No evaluado";
  return mapping[val] || "No evaluado";
}

const mapClaridad = { "Claro": "Experto", "Poco claro": "Aceptable", "Confuso": "Aprendiz" };
const mapCoherencia = { "Coherente": "Experto", "Parcialmente coherente": "Aceptable", "Incoherente": "Aprendiz" };
const mapPrecision = { "Precisa": "Experto", "Imprecisa": "Aceptable" };
const mapCalidadTec = { "Alta": "Experto", "Media": "Capacitado", "Baja": "Aceptable" };
const mapFluidez = { "Fluido": "Experto", "Comprensible": "Capacitado", "Poco fluido": "Aprendiz" };
const mapComprensibilidad = { "Alta": "Experto", "Media": "Capacitado", "Baja": "Aceptable" };
const mapIdentifica = { "Claro": "Experto", "Con dificultad": "Capacitado", "Con errores": "Aceptable", "No identifica": "Aprendiz" };
const mapCoherenciaPC = { "Coherente": "Experto", "Parcialmente coherente": "Capacitado", "Incoherente": "Aprendiz" };

// Niveles desde Ollama
const nivelClaridad = mapToLevel(analisis_relato.claridad, mapClaridad);
const nivelCoherencia = mapToLevel(analisis_relato.coherencia, mapCoherencia);
const nivelPrecision = mapToLevel(analisis_relato.precision, mapPrecision);
const nivelCalidadTec = mapToLevel(analisis_audio.calidad_tecnica, mapCalidadTec);
const nivelFluidez = mapToLevel(analisis_audio.fluidez, mapFluidez);
const nivelComprensib = mapToLevel(analisis_audio.comprensibilidad, mapComprensibilidad);
const nivelIdentifica = mapToLevel(analisis_parrafo.nivel_identificacion, mapIdentifica);
const nivelCoherenciaPC = mapToLevel(analisis_parrafo.coherencia_analisis, mapCoherenciaPC);

// ===== DATOS DEL PROCESSOR =====
const metrics = data.metrics || {};
const segments = data.segments || {};
const evaluation = data.evaluation || {};
const cog = evaluation.cognitivo || {};
const act = evaluation.actitudinal || {};
const com = evaluation.comunicativo || {};
const pen = evaluation.pensamiento_critico || {};
const orig = evaluation.originalidad || {};
const erroresOrto = com.errores_ortografia_puntuacion;
const erroresDetalle = com.errores_detalle || [];
const historia = segments.historia || { text: "", word_count: 0 };
const enlace = segments.enlace || { text: "", url: "" };
const parrafo = segments.parrafo_comparacion || { text: "", word_count: 0, line_count: 0 };
const transcripcion = segments.transcripcion_audio || { text: "", error: null };
const highlights = data.highlights_tabla || [];
const highlightsTotal = data.highlights_total || 0;
const audioDuration = data.audio_duration_seconds;
const durationStr = audioDuration != null ? `${Math.floor(audioDuration / 60)} min ${Math.round(audioDuration % 60)} s` : "—";
const relato = cog.relato_escrito || {};
const clases = cog.clases_palabras || {};
const audio = cog.audio || {};
const parrafoOE = cog.parrafo_oral_escrito || {};

// ===== CONSTRUIR REPORTE =====
const nombreEstudiante = (() => {
  const partes = filename.split("_");
  return (partes.length >= 2 && partes[1]) ? partes[1] : "Estudiante";
})();

let report = "";
if (data.error) {
  report = `# ❌ ERROR DE PROCESAMIENTO\n\n${data.error}\n${data.details || ""}`;
} else {

// --- Sección 1: Validaciones ---
const sec1 = `### 1. 📂 Validaciones
- **Nombre de archivo:** ${data.filename_valid ? "✅ Correcto" : "❌ Revisar formato (Apellidos_Nombre_M02S1AI2)"}
- **Historia de vida:** **${historia.word_count}** palabras (${metrics.story_length?.status || "N/A"})
  - Rango esperado: 350–1000 palabras (1–2 cuartillas, Arial 12)`;

// --- Sección 2: Segmentos detectados ---
const sec2 = `### 2. 📜 Segmentos detectados

#### Historia (relato)
- Palabras: **${historia.word_count}**
${historia.text ? `- *Vista previa:* ${historia.text.slice(0, 200)}…` : "- *Sin texto detectado*"}

#### Enlace al audio
- **URL:** ${segments.audio_url ? `✅ \`${segments.audio_url}\`` : "❌ No encontrada"}
${enlace.text ? `- *Párrafo:* ${enlace.text.slice(0, 120)}…` : ""}

#### Párrafo de reflexión (diferencias oral/escrita)
- Palabras: **${parrafo.word_count}** (${metrics.comparison_length?.status || "N/A"})
  - Esperado: 3–14 líneas (~30–180 palabras) — *Rúbrica v4 flexible*
${parrafo.text ? `- *Vista previa:* ${parrafo.text.slice(0, 200)}…` : "- *Sin texto detectado*"}`;

// --- Sección 3: Análisis de Historial ---
const sec3 = `### 3. Análisis de Historial (relato)
#### Organización de la información

- **Claridad** ¿Se entiende el relato sin releer?
\t${analisis_relato.claridad || "No evaluado"}${analisis_relato.extracto_claridad ? ` — "${analisis_relato.extracto_claridad}"` : ""}

- **Coherencia** ¿Las ideas siguen un hilo lógico?
\t${analisis_relato.coherencia || "No evaluado"}${analisis_relato.extracto_coherencia ? ` — "${analisis_relato.extracto_coherencia}"` : ""}

- **Precisión** ¿Las expresiones transmiten bien la idea?
\t${analisis_relato.precision || "No evaluado"}${analisis_relato.extracto_precision ? ` — "${analisis_relato.extracto_precision}"` : ""}

#### Análisis gramatical (colores)
- **Palabras con color:** ${highlightsTotal}
- **Aciertos:** ${clases.correctas ?? 0} de ${clases.total ?? 0} (**${clases.pct_correctas ?? 0}%**)

| Palabra | Clase requerida | Detectada | Resultado |
|---------|-----------------|-----------|-----------|
${highlights.slice(0, 35).map(h => `| ${h.word} | ${h.category} | ${h.pos_detected} | ${h.match ? "✅" : "❌"} |`).join("\n")}
${highlightsTotal > 35 ? "| … | … | … | … |" : ""}`;

// --- Sección 4: Análisis de Audio ---
const sec4 = `### 4. Análisis de Audio
- **Audio (URL):** ${segments.audio_url ? "✅ Sí" : "❌ No"}
- **Transcripción:** ${transcripcion.text ? "✅ Incluida" : `❌ ${transcripcion.error || "No disponible"}`}
- **Extensión reflexión:** **${parrafo.word_count}** palabras
- **Tiempo**: ${durationStr}
- **Claridad técnica del audio:** ${analisis_audio.calidad_tecnica || "No evaluado"}
- **Comprensibilidad:** ${analisis_audio.comprensibilidad || "No evaluado"}
- **Fluidez del discurso:** ${analisis_audio.fluidez || "No evaluado"}
- **¿Lee o narra?:** ${analisis_audio.lee_o_narra || "No determinado"}
${analisis_audio.observaciones ? `- **Observaciones:** ${analisis_audio.observaciones}` : ""}
${transcripcion.text ? `\n**Texto transcrito (narración oral):**\n\n${transcripcion.text}\n` : ""}`;

// --- Sección 5: Análisis del párrafo ---
const sec5 = `### 5. Análisis del párrafo de reflexión
- **Párrafo presente:** ${parrafoOE.existe ? "✅ Sí" : "❌ No"}
- **Identifica diferencias:** ${analisis_parrafo.identifica_diferencias ? "✅ Sí" : "❌ No"} (${analisis_parrafo.nivel_identificacion || "—"})
${analisis_parrafo.extractos ? `\t${analisis_parrafo.extractos}` : ""}
- **Coherencia del análisis:** ${analisis_parrafo.coherencia_analisis || "No evaluado"}`;

// --- Sección 6: Ortografía ---
const sec6 = `### 6. Análisis de ortografía
- **Errores detectados:** ${erroresOrto != null ? `**${erroresOrto}**` : "No calculado"}
${erroresOrto != null ? `- Nivel sugerido: ${com.nivel_ortografia || "—"}` : `- ${com.nota || "Revisar con LenguageTool"}`}
${erroresDetalle.length ? `\n**Detalle de errores (ortografía/gramática):**\n\n${erroresDetalle.map((e, i) => `${i+1}. **${String(e.message || "—").replace(/\n/g, " ")}**\n   Contexto: "${String(e.contexto || "").replace(/\n/g, " ").replace(/"/g, "'")}"\n   Sugerencia: ${e.sugerencia ? '"' + String(e.sugerencia).replace(/\n/g, " ").replace(/"/g, "'") + '"' : "—"}`).join("\n\n")}` : ""}`;

// --- Sección 7: Evaluación (tablas por criterio) ---
const sec7 = `### 7. Evaluación

#### CRITERIO: Cognitivo
**Relato escrito**

| Métrica | Contiene | Esperado | Nivel |
|---------|----------|----------|-------|
| Extensión (cuartillas) | ${relato.cuartillas || "—"} | 1-2 | ${relato.nivel || "—"} |
| Extensión (palabras) | ${relato.palabras || 0} | 280-1100 | ${relato.nivel || "—"} |
| Fuente | ${relato.fuente_ok ? "Arial 12 pts" : "Diferente"} | Arial 12 | ${relato.fuente_ok ? "Experto" : "Aceptable"} |
| Título | ${relato.titulo_ok ? "✅" : "❌"} | ✅ | ${relato.titulo_ok ? "Experto" : "Aceptable"} |

**Clases de palabras (colorización)**

| Métrica | Contiene | Esperado | Nivel |
|---------|----------|----------|-------|
| Párrafo seleccionado | ${(clases.total || 0) > 0 ? "✅" : "❌"} | ✅ | ${(clases.total || 0) > 0 ? "Experto" : "Requiere Apoyo"} |
| % palabras correctamente clasificadas | ${clases.pct_correctas ?? 0}% | ≥85% | ${clases.nivel || "—"} |

**Audio**

| Métrica | Contiene | Esperado | Nivel |
|---------|----------|----------|-------|
| Grabación presente | ${audio.presente ? "✅" : "❌"} | ✅ | ${audio.presente ? "Experto" : "Requiere Apoyo"} |
| Liga en documento | ${audio.liga_ok ? "✅" : "❌"} | ✅ | ${audio.liga_ok ? "Experto" : "Requiere Apoyo"} |
| Duración | ${durationStr} | 90-240 s | ${audio.nivel || "—"} |

**Párrafo oral/escrito**

| Métrica | Contiene | Esperado | Nivel |
|---------|----------|----------|-------|
| Existe párrafo | ${parrafoOE.existe ? "✅" : "❌"} | ✅ | ${parrafoOE.existe ? "Experto" : "Requiere Apoyo"} |
| Extensión (líneas) | ${parrafoOE.lineas || 0} | 3-14 | ${parrafoOE.nivel || "—"} |

#### CRITERIO: Actitudinal

| Métrica | Contiene | Esperado | Nivel |
|---------|----------|----------|-------|
| Indicaciones cumplidas | ${act.cumplidos ?? 0}/12 | 10/12 | ${act.nivel || "—"} |

#### CRITERIO: Comunicativo
**Organización de la información**

| Métrica | Contiene | Esperado | Nivel |
|---------|----------|----------|-------|
| Claridad | ${analisis_relato.claridad || "—"} | Claro | ${nivelClaridad} |
| Coherencia | ${analisis_relato.coherencia || "—"} | Coherente | ${nivelCoherencia} |
| Precisión | ${analisis_relato.precision || "—"} | Precisa | ${nivelPrecision} |

**Netiqueta**

| Métrica | Contiene | Esperado | Nivel |
|---------|----------|----------|-------|
| Normas de comunicación virtual | ✅ | ✅ | Experto |

**Errores de ortografía**

| Métrica | Contiene | Esperado | Nivel |
|---------|----------|----------|-------|
| Errores de sintaxis, ortografía y puntuación | ${erroresOrto != null ? erroresOrto : "No calculado"} | 0-2 | ${com.nivel_ortografia || "—"} |

**Calidad del audio/video y discurso oral**

| Métrica | Contiene | Esperado | Nivel |
|---------|----------|----------|-------|
| Calidad técnica | ${analisis_audio.calidad_tecnica || "—"} | Alta | ${nivelCalidadTec} |
| Fluidez del discurso | ${analisis_audio.fluidez || "—"} | Fluido | ${nivelFluidez} |
| Comprensibilidad | ${analisis_audio.comprensibilidad || "—"} | Alta | ${nivelComprensib} |

#### Criterio Pensamiento Crítico
**Diferencia oral/escrito**

| Métrica | Contiene | Esperado | Nivel |
|---------|----------|----------|-------|
| Identifica diferencias | ${analisis_parrafo.identifica_diferencias ? "✅" : "❌"} | ✅ | ${nivelIdentifica} |
| Coherencia del análisis | ${analisis_parrafo.coherencia_analisis || "—"} | Coherente | ${nivelCoherenciaPC} |

**Clases de palabras**

| Métrica | Contiene | Esperado | Nivel |
|---------|----------|----------|-------|
| Comprensión de clasificación | ${pen.clases_palabras?.comprende ? "Comprende" : "No comprende"} | Comprende | ${pen.clases_palabras?.nivel || "—"} |

#### Indicador de Revisión (Originalidad)

| Métrica | Contiene | Esperado | Nivel |
|---------|----------|----------|-------|
| Contenido original y desarrollo de ideas propias | ${!orig.indicadores_ia?.frases_tipicas_count ? "Excelente" : "Revisar"} | Excelente | ${!orig.indicadores_ia?.frases_tipicas_count ? "Excelente" : "Revisar"} |
| Libre de cualquier tipo de plagio | Excelente | Excelente | Excelente |
| Ideas sustentadas con fuentes confiables | Excelente | Excelente | Excelente |
| Incluye citas y referencias (Manual PL-SEP) | No aplica | No aplica | No aplica |

#### Valoración global

| Criterio | Nivel |
|----------|-------|
| Cognitivo | ${cog.nivel_global || "—"} |
| Actitudinal | ${act.nivel || "—"} |
| Comunicativo | ${com.nivel_ortografia || "—"} |
| Pensamiento crítico | ${pen.clases_palabras?.nivel || "—"} |
| Originalidad | Excelente |`;

report = `# REPORTE DE EVALUACIÓN: ${filename}
*Script v4 – Análisis modular (Python + Ollama)*

---

${sec1}

---

${sec2}

---

${sec3}

---

${sec4}

---

${sec5}

---

${sec6}

---

${sec7}

---
*Reporte generado por n8n (flujo v4)*
`;
} // fin del if/else error

// ===== CONSTRUIR EVALUACIÓN (para ChatGPT) =====
const indicacionesLabels = [
  "Relato sobre historia de vida", "Extensión 1-2 cuartillas (350-1000 palabras)", "Fuente Arial 12 pt",
  "Título 'El relato de mi historia'", "Párrafo con clases de palabras coloreadas",
  "Colores correctos (verbos verde, etc.)", "Grabación audio/video", "Duración 3 min (+/- 30s)",
  "Carga en nube", "Liga al final del documento", "Párrafo diferencias 5-10 líneas",
  "Nombre archivo Apellidos_Nombre_M02S1AI2"
];
const indicaciones = act.indicaciones || [];
const cumplidos = act.cumplidos ?? 0;
const resumenLLM = evaluation.resumen_llm || [];
const filenameValid = indicaciones[11];

// Frases sugeridas
const frases = [];
if (relato.extension_ok && relato.titulo_ok && relato.fuente_ok) {
  frases.push("Relato: \"tu relato se ha apegado al formato y la extensión solicitados (1 a 2 cuartillas)\".");
} else {
  const pal = relato.palabras || 0;
  if (!relato.extension_ok) {
    if (pal < 350) frases.push(`Relato: \"tu relato es breve (${pal} palabras); te sugiero ampliarlo a una extensión mínima de una cuartilla (350-1000 palabras)\".`);
    else if (pal > 1000) frases.push(`Relato: \"tu relato excede la extensión solicitada (${pal} palabras); considera condensar para mantenerte en el rango de 1 a 2 cuartillas\".`);
  }
  if (!relato.titulo_ok) frases.push("Relato título: \"no olvides titular tu relato como 'El relato de mi historia'\".");
  if (!relato.fuente_ok) frases.push("Relato fuente: \"recuerda usar fuente Arial de 12 puntos\".");
  if (relato.extension_ok && (!relato.titulo_ok || !relato.fuente_ok)) frases.push("Relato: \"tu relato cumple con la extensión, pero revisa el formato (título/fuente)\".");
}
const pct = clases.pct_correctas;
if (pct != null) {
  if (pct >= 100) frases.push("Clases: \"has identificado correctamente todas las clases de palabras\".");
  else if (pct >= 85) frases.push("Clases: \"has identificado correctamente la mayoría de las clases de palabras; revisa los casos con confusión\".");
  else if (pct >= 75) frases.push("Clases: \"identificaste gran parte; te sugiero repasar adverbios y preposiciones\".");
  else if (pct >= 65) frases.push("Clases: \"hay varias sin clasificar correctamente; revisa el material sobre clases de palabras\".");
  else frases.push("Clases: \"es importante repasar verbos, sustantivos, adjetivos, adverbios, artículos y preposiciones\".");
}
if (audio.liga_ok && audio.duracion_ok) frases.push("Audio: \"grabaste un relato con la duración solicitada (3 min) y compartiste correctamente la liga\".");
else if (audio.liga_ok) {
  const dur = audio.duracion_segundos || 0;
  if (dur > 0 && dur < 150) frases.push(`Audio: \"compartiste la liga correctamente; sin embargo, tu audio es corto (${Math.round(dur)}s). Procura que dure entre 2:30 y 3:30 min\".`);
  else if (dur > 210) frases.push(`Audio: \"compartiste la liga correctamente; sin embargo, tu audio excede el tiempo (${Math.round(dur)}s). Procura que sea de 3 min (+/- 30s)\".`);
  else frases.push("Audio: \"compartiste la liga correctamente; procura que la duración se mantenga cercana a los 3 minutos\".");
}
else if (audio.presente) frases.push("Audio: \"no encontré la liga o no funciona; recuerda que es requisito incluir el enlace compartido en la nube\".");
else frases.push("Audio: \"no se encontró la liga de tu grabación; es indispensable para evaluar tu expresión oral\".");
if (analisis_audio.lee_o_narra === "Lee") frases.push("Audio: \"noté que leíste el texto; es importante narrarlo de forma natural\".");
else if (analisis_audio.lee_o_narra === "Narra") frases.push("Audio: \"narraste tu historia de manera fluida y natural\".");
if (parrafoOE.existe && parrafoOE.extension_ok) frases.push("Párrafo: \"escribiste un párrafo con la extensión solicitada sobre las diferencias\".");
else if (parrafoOE.existe) frases.push("Párrafo: \"incluiste el párrafo; ajusta la extensión a 5-10 líneas\".");
else frases.push("Párrafo: \"no encontré el párrafo sobre diferencias oral/escrita\".");
if (filenameValid) frases.push("Técnico: \"enviaste correctamente el archivo con el nombre solicitado\".");
else frases.push("Técnico: \"el nombre del archivo no coincide con el formato; usa Apellidos_Nombre_M02S1AI2\".");

// Organización (de Ollama)
if (analisis_relato.claridad === "Claro" && analisis_relato.coherencia === "Coherente") {
  frases.push("Comunicativo: \"organizas la información de manera clara, coherente y precisa\".");
} else {
  frases.push(`Comunicativo: \"la organización podría mejorar (claridad: ${analisis_relato.claridad || '—'}, coherencia: ${analisis_relato.coherencia || '—'})\".`);
}

// Áreas de mejora y recursos
const areasMejora = [];
if (pct != null && pct < 85) areasMejora.push("Clases de palabras");
if (!audio.duracion_ok || !parrafoOE.existe) areasMejora.push("Comunicación oral vs escrita");
if (!relato.extension_ok || !relato.titulo_ok || !relato.fuente_ok) areasMejora.push("Redacción / relato narrativo");
if (erroresOrto != null && erroresOrto > 2) areasMejora.push("Ortografía");
if (areasMejora.length === 0) areasMejora.push("General / Pensamiento crítico");
const areasUnicas = [...new Set(areasMejora)];

const recursosPorArea = {
  "Clases de palabras": [
    "Clases de palabras (CCH-UNAM): https://e1.portalacademico.cch.unam.mx/alumno/tlriid2/unidad1/catGramaticales/clasesDePalabras1",
    "Adjetivos más usados: https://aprendehablando.com/los-50-adjetivos-mas-usados-en-espanol/",
    "La oración (estructura): https://e1.portalacademico.cch.unam.mx/alumno/tlriid2/unidad1/catGramaticales/laOracion",
    "Clases y subclases de palabras (RAE): https://www.rae.es/gramatica-basica/determinantes-y-pronombres/clases-y-subclases-de-palabras",
  ],
  "Ortografía": [
    "LenguageTool – Tutorial: https://youtu.be/Zg4Ua3G8wkU",
    "LanguageTool corrector: https://languagetool.org/es/corrector-ortografico-espanol",
  ],
  "Comunicación oral vs escrita": [
    "Oralidad y Escritura (CCH): https://portalacademico.cch.unam.mx/alumno/tlriid1/unidad2/dialogo/oralidadYescritura",
    "De lo oral a lo escrito (SEP): https://nuevaescuelamexicana.sep.gob.mx/contenido/coleccion/de-lo-oral-a-lo-escrito/",
    "AprendeEnCasa – Narramos en forma escrita (SEP): https://www.youtube.com/watch?v=KtY5Gy77Ck8",
  ],
  "Redacción / relato narrativo": [
    "Secuencia del relato (CCH): https://portalacademico.cch.unam.mx/alumno/tlriid1/unidad4/secuenciaRelato",
    "La autobiografía (UNAM): http://uapas2.bunam.unam.mx/humanidades/la_autobiografia/",
    "Cómo hacer una historia de vida: http://laaventuradeaprender.intef.es/guias/proyectos-colaborativos/como-hacer-una-historia-de-vida",
    "Pasos para elaborar un relato (PDF): http://saeta.uemstaycm.sems.gob.mx/content/docs/C1_M1_S1_Relato_PDF.pdf",
    "Redacto, reviso y corrijo mi cuento (SEP): https://nuevaescuelamexicana.sep.gob.mx/contenido/coleccion/redacto-reviso-y-corrijo-mi-cuento-2/",
  ],
  "General / Pensamiento crítico": [
    "Participación en foro aprendiendo y espacios abiertos (Prepa en Línea-SEP).",
  ]
};
let recursosTexto = "";
areasUnicas.forEach(area => {
  const links = recursosPorArea[area];
  if (links && links.length) {
    recursosTexto += `\n- **${area}:**\n${links.map(l => `  - ${l}`).join("\n")}`;
  }
});
if (!recursosTexto) recursosTexto = "\n- **General:** Participación en foro aprendiendo y espacios abiertos.";

const evaluacionContent = data.error ? "" : `# Evaluación para retroalimentación: ${filename}
*Métricas v4 (flexibles) – Rúbrica M2 AI2*

## Nombre del estudiante
**${nombreEstudiante}** (usar en "Hola [nombre]:")

## Indicaciones (${cumplidos}/12)
${indicacionesLabels.map((l, i) => `- ${indicaciones[i] ? "✅" : "☐"} ${l}`).join("\n")}

## Niveles sugeridos (v4 flexible)
- **Cognitivo:** ${cog.nivel_global || "—"} (${cog.puntaje_global ?? "—"} pts)
- **Actitudinal:** ${act.nivel || "—"} (${act.puntaje ?? "—"} pts)
- **Comunicativo (ortografía):** ${com.nivel_ortografia || "—"} (${com.puntaje_ortografia ?? "—"} pts)

## Análisis cualitativo (Ollama)
- **Organización del relato:** Claridad=${analisis_relato.claridad || "—"}, Coherencia=${analisis_relato.coherencia || "—"}, Precisión=${analisis_relato.precision || "—"}
  - *Extracto a mejorar:* "${analisis_relato.extracto_mejorable || ""}"
  - *Punto fuerte detectado:* "${analisis_relato.punto_fuerte || ""}"
- **Audio:** Calidad=${analisis_audio.calidad_tecnica || "—"}, Fluidez=${analisis_audio.fluidez || "—"}, Lee/Narra=${analisis_audio.lee_o_narra || "—"}
  - *Punto fuerte oral:* "${analisis_audio.punto_fuerte_oral || ""}"
- **Párrafo reflexión:** Identifica=${analisis_parrafo.identifica_diferencias ? "Sí" : "No"}, Coherencia=${analisis_parrafo.coherencia_analisis || "—"}
  - *Extractos clave del párrafo:* "${analisis_parrafo.extractos || ""}"

## Métricas completas (input para IA)
\`\`\`
${resumenLLM.join("\n")}
Ollama – Claridad: ${analisis_relato.claridad || "—"}, Coherencia: ${analisis_relato.coherencia || "—"}, Precisión: ${analisis_relato.precision || "—"}
Ollama – Audio calidad: ${analisis_audio.calidad_tecnica || "—"}, Fluidez: ${analisis_audio.fluidez || "—"}, Lee/Narra: ${analisis_audio.lee_o_narra || "—"}
Ollama – Párrafo: identifica=${analisis_parrafo.identifica_diferencias}, coherencia=${analisis_parrafo.coherencia_analisis || "—"}
\`\`\`

## Frases sugeridas
${frases.join("\n")}

## Recursos sugeridos por área de mejora
Áreas: ${areasUnicas.join(", ")}.
${recursosTexto}
`;

return [{
  json: {
    filename,
    report,
    evaluacion: evaluacionContent,
    status: data.error ? "error" : "success"
  }
}];
```

**Nota:** Ajustar `$('v4 Extract Audio')` al nombre exacto del nodo 9 en tu flujo.

---

## Nodo 12 – v4 Guardar Reporte

- **Tipo:** Execute Command
- **Comando:**

```bash
cat <<'REPORTEOF' > "/home/node/reportes/Reporte_{{ $json.filename }}.md"
{{ $json.report }}
REPORTEOF
```

---

## Nodo 13 – v4 Guardar Evaluación

- **Tipo:** Execute Command
- **Comando:**

```bash
cat <<'EVALEOF' > "/home/node/reportes/Evaluacion_{{ $json.filename }}.md"
{{ $json.evaluacion }}
EVALEOF
```

---

## Nodo 14 – v4 Prep ChatGPT (Code)

Construye el prompt para ChatGPT con ejemplo completo (few-shot).

```javascript
const EJEMPLO_RETRO = `Hola Sherlyn:

Espero que esta actividad te haya ayudado a recordar las clases de palabras y a diferenciar entre la comunicación escrita y la oral. Identificar verbos, sustantivos, adjetivos, adverbios, artículos y preposiciones es muy útil en la vida cotidiana, ya que mejora tu capacidad de comprender y utilizar el lenguaje de manera efectiva. Además, distinguir entre la comunicación escrita y oral te permitirá comunicarte de manera más adecuada en distintas situaciones. Has demostrado un buen nivel de comprensión, pero con un poco más de esfuerzo, podrías profundizar aún más en estos temas y mejorar tu desempeño. Reconozco tu esfuerzo en realizar la actividad y en seguir las normas de netiqueta para la comunicación en entornos virtuales de aprendizaje.

En el primer ejercicio, tu relato sobre la historia de tu vida ha sido interesante y se ha apegado al formato y la extensión solicitados. Me pareció muy emotivo cuando mencionas: "desde muy pequeña soñaba con ser enfermera para ayudar a los demás", pues este tipo de fragmentos dan mucha fuerza y autenticidad a tu narrativa. Para futuros relatos, sería útil que consideres el uso de descripciones aún más detalladas y diálogos que enriquezcan la historia para el lector.

En el ejercicio 2, has demostrado una buena capacidad para identificar correctamente todas las clases de palabras. Este conocimiento es fundamental porque te permite comprender mejor cómo se estructura el lenguaje y cómo cada parte contribuye al significado de una oración.

Para el ejercicio 3, grabaste un relato de tu vida. Sin embargo, noté que lo leíste en lugar de narrarlo de forma natural. Es importante realizar el relato sin leerlo, ya que esto te permite experimentar las diferencias entre la elaboración de un relato escrito y uno oral. Te sugiero que hagas un esquema y practiques varias veces para sentirte más cómodo con el contenido.

En el ejercicio final, escribiste un párrafo con la extensión solicitada sobre las diferencias entre la expresión oral y escrita. Las diferencias que mencionas son interesantes, particularmente cuando señalas que "[extracto de ejemplo del alumno]", ya que demuestras una reflexión profunda sobre cómo la entonación cambia el sentido del mensaje. Aunque se te da muy bien la expresión escrita, no olvides seguir trabajando en la expresión oral para fortalecer aún más tus habilidades en ambas áreas.

Por otro lado, puedo ver que has empleado la tecnología para generar tu documento con toda la información solicitada, siguiendo todas las instrucciones para la elaboración de la actividad. Enviaste correctamente el archivo en el espacio destinado y lo has nombrado como se solicita en las instrucciones. Has entregado en el tiempo establecido tu documento, sin algún retraso.

En cuanto al criterio comunicativo, organizas toda la información de manera clara, coherente y precisa. No presentas errores en sintaxis, ortografía o puntuación, y presentas las ideas de manera lógica y congruente. Recuerda que siempre puedes utilizar revisores de ortografía como LenguageTool para revisar tus escritos. Te dejo un tutorial para que veas cómo utilizarlo: https://youtu.be/Zg4Ua3G8wkU.

Respecto al criterio de Pensamiento Crítico, tu trabajo muestra un buen inicio en la identificación de las diferencias entre la comunicación oral y escrita. Sería útil profundizar más en estos temas, así como en la clasificación de verbos, sustantivos, adjetivos, adverbios, artículos y preposiciones. Te sugiero revisar estos conceptos con mayor detenimiento y participar en el foro aprendiendo, así como en los espacios abiertos para ver diferentes perspectivas y aplicaciones prácticas.

Después de haber visto este tema me parece que este recurso podría complementar lo que vimos. Te puede ayudar a profundizar en las categorías gramaticales, y cómo las puedes manejar de la mejora manera. Te recomiendo revisarlo:
https://e1.portalacademico.cch.unam.mx/alumno/tlriid2/unidad1/catGramaticales/clasesDePalabras1

Como cierre, considerando lo aprendido en esta unidad, ¿cómo podrías conectar lo visto sobre comunicación oral y escrita con situaciones reales en tu vida diaria? Lo has hecho bien, reconozco tu esfuerzo y dedicación. El aprendizaje es continuo, cada paso cuenta en tu desarrollo académico, sigue adelante con determinación, tu dedicación es clave para alcanzar metas. Me despido reiterando mi reconocimiento por tu esfuerzo y poniéndome a tu disposición por si tuvieras alguna duda respecto a tu calificación o retroalimentación.

Saludos,

Ricardo Raúl Estrada Pérez
Asesor Virtual
M2C1G82-021.`;

const instruccion = `Tu tarea: genera UNA retroalimentación para el estudiante cuyos datos aparecen más abajo. La retroalimentación debe seguir EXACTAMENTE la misma estructura, longitud, tipo de párrafos y transiciones que el siguiente ejemplo. Usa el NOMBRE del estudiante que viene en los datos. Usa las FRASES SUGERIDAS y los RECURSOS listados. Escribe solo el texto de la retroalimentación. Español de México.

=== EJEMPLO DE REFERENCIA ===

${EJEMPLO_RETRO}

=== FIN DEL EJEMPLO ===

DATOS DEL ESTUDIANTE:

`;

const data = $json || {};
const evaluacion = data.evaluacion || "";
const userMessage = instruccion + evaluacion;

const systemMessage = `Eres un asesor virtual de Prepa en Línea-SEP para la actividad "Mi Historia de Vida" (M2 AI2). Genera retroalimentación personalizada siguiendo la estructura del ejemplo. Usa las frases sugeridas y recursos de los datos. Incluye despedida: Saludos, Ricardo Raúl Estrada Pérez, Asesor Virtual, M2C1G82-021. Responde solo con el texto de la retroalimentación.`;

const bodyForOpenAI = {
  model: "gpt-4o-mini",
  messages: [
    { role: "system", content: systemMessage },
    { role: "user", content: userMessage }
  ],
  max_tokens: 2048,
  temperature: 0.7
};

return [{
  json: {
    ...data,
    bodyForOpenAI: JSON.stringify(bodyForOpenAI)
  }
}];
```

---

## Nodo 15 – v4 ChatGPT (HTTP Request)

- **Tipo:** HTTP Request
- **Método:** POST
- **URL:** `https://api.openai.com/v1/chat/completions`
- **Headers:**
  - `Content-Type`: `application/json`
  - `Authorization`: `Bearer TU_OPENAI_API_KEY`
- **Body:** Send Body → Raw → Content-Type: `application/json`
- **Body (Expression):** `{{ $json.bodyForOpenAI }}`
- **Timeout:** 180 s
- **Settings:** Continue On Fail = ✅

---

## Nodo 15b – v4 Merge ChatGPT

- **Tipo:** Merge
- **Entrada 1:** nodo **14** (v4 Prep ChatGPT)
- **Entrada 2:** nodo **15** (v4 ChatGPT)
- **Modo:** Combine / Merge By Position

---

## Nodo 16 – v4 Extract ChatGPT (Code)

```javascript
const data = $json || {};
let texto = "";
const msg = data.choices?.[0]?.message || data.body?.choices?.[0]?.message;
if (msg?.content) texto = msg.content;
if (texto && typeof texto === "string") {
  texto = texto.replace(/\\n/g, "\n");
}
const filename = (data.filename || data.json?.filename || "SinNombre").replace(/\.docx$/i, "").trim();
return [{ json: { filename, retroalimentacion: texto || "(No se pudo generar la retroalimentación con ChatGPT.)" } }];
```

---

## Nodo 17 – v4 Guardar Retroalimentación

- **Tipo:** Execute Command
- **Comando:**

```bash
cat <<'RETROEOF' > "/home/node/reportes/Retroalimentacion_{{ $json.filename }}_ChatGPT.md"
{{ $json.retroalimentacion }}
RETROEOF
```

---

## Nodo 18 – v4 Copiar a procesados

- **Tipo:** Execute Command
- **Entrada:** salida del nodo 12.
- **Comando:**

```bash
mkdir -p /home/node/entradas/procesados && cp "{{ $('n3_Split Files').item.json.filePath }}" /home/node/entradas/procesados/
```

Ajustar `'v4 Split Files'` al nombre real del nodo 3.

---

## Nodo 19 – v4 Concatenar Todo (Code)

Une el reporte, la evaluación y la retroalimentación en un solo documento Markdown.

```javascript
// No es necesario que el nodo 17 esté conectado directamente a este nodo, ya que la retroalimentación se pasa como input.
const node11 = $('n11_Build Report + Evaluación').item.json;
const report = node11.report;
const evaluacion = node11.evaluacion;
const retro = $json.retroalimentacion;
const filename = $json.filename;

const finalContent = `# EXPEDIENTE DE EVALUACIÓN: ${filename}

---

## 1. REPORTE DE MÉTRICAS (AUTOMÁTICO)
${report}

---

## 2. EVALUACIÓN CUALITATIVA (PARA ASESOR)
${evaluacion}

---

## 3. RETROALIMENTACIÓN FINAL (IA)
${retro}

---
*Generado automáticamente por el flujo v4.*
`;

return {
  filename,
  finalContent
};
```

---

## Nodo 20 – v4 Guardar Todo (Execute Command)

- **Tipo:** Execute Command
- **Comando:**

```bash
cat <<'EOF' > "/home/node/reportes/Completo_{{ $json.filename }}.md"
{{ $json.finalContent }}
EOF
```

---

## Resumen de conexiones

```
1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11
11 → 12 (guardar reporte)
11 → 13 (guardar evaluación)
11 → 14 (prep ChatGPT)
12 → 18 (copiar a procesados)
14 → 15 (HTTP ChatGPT)
14 → 15b (Merge input 1)
15 → 15b (Merge input 2)
15b → 16 (extraer respuesta)
16 → 17 (guardar retroalimentación)
17 → 19 (concatenar todo)
19 → 20 (guardar unificado)
```

---

## Comportamiento ante errores

- **Ollama falla:** Con "Continue On Fail" en nodos 6, 8, 10, los Code de extracción (7, 9, 11) usan valores por defecto ("No evaluado"). El reporte se genera igualmente con las métricas de Python.
- **ChatGPT falla:** Nodos 12, 13 y 18 siguen funcionando. Solo 17 tendrá un texto de error.
- **Processor falla:** Nodo 11 detecta `data.error` y genera un reporte de error.

---

## Scripts Python v4

Los scripts se montan en `/home/node/scripts/` (volumen Docker):

| Script | Descripción |
|--------|-------------|
| `processor_v4.py` | Procesador principal v4: envuelve processor.py + métricas flexibles |
| `evaluation_rubric_v4.py` | Rúbrica con umbrales tolerantes |
| `processor.py` | Procesador base v3 (reutilizado por v4) |
| `evaluation_rubric.py` | Rúbrica v3 (no modificada) |
| `ai_indicators.py` | Detección de indicadores IA |
| `orthography_check.py` | LanguageTool API |
| `audio_transcribe.py` | Descarga y transcripción de audio |

No se modifica ningún script existente. Los v4 importan de los v3.

---

## Notas de configuración

1. **Nombres de nodos:** Los Code nodes referencian nodos anteriores por nombre (ej. `$('v4 Parse Métricas')`). Si renombras un nodo, actualiza las referencias en los Code posteriores.

2. **Modelo Ollama:** Cambiar `"model": "mistral"` en los Code nodes 5, 7, 9 si usas otro modelo.

3. **API key OpenAI:** Configurar en el nodo 15 (Header Authorization) o como variable de entorno en n8n.

4. **Timeouts:** Los HTTP Request de Ollama tienen 120 s; el de ChatGPT 180 s. Ajustar si es necesario.

5. **Orden de ejecución:** La cadena Ollama es secuencial (relato → audio → párrafo) para simplificar el flujo. Si quieres paralelizar, usar 3 HTTP en paralelo desde nodo 5 + 2 Merge nodes para combinar.

---

## Referencias

- Flujo base (v3): docs/01_guias/20260209_flujo_antigrav_v3_ollama_codigos.md
- Métricas: docs/01_guias/m2_ai2_metricas_evaluacion.md
- Retroalimentación: docs/01_guias/m2_ai2_retroalimentacion.md
- Ejemplo de reporte: docs/01_guias/20260210_guia_ejemplo_reporte.md

**Versión:** 4.0 (flujo modular: Python + Ollama cualitativo + ChatGPT retroalimentación)
**Fecha:** 2026-02-10
