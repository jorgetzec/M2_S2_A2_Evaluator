---
Title: "Resumen de mejoras funcionales (M2 AI2)"
Filename: "bitacora_04_mejoras_app"
Date: 2026-04-22
Author: Jorge A. Trec-Interián
Language_stack: ["Python", "Docker"]
Tools: ["Streamlit", "PyMuPDF (fitz)", "python-docx", "spaCy", "Gemini Pro"]
Objectives: "Consolidar la extracción de entregas, métricas, rúbrica M2 AI2 y retroalimentación estructurada con IA; además de mejorar la UX del asesor con segmentación y export."
tags: ["streamlit", "evaluacion", "ocr", "transcripcion", "segmentacion", "ia", "gemini"]
Description: "Actualización integral del motor de procesamiento de PDF, detección de colores personalizados (pasteles/vibrantes), flexibilización gramatical y mejora en la persistencia de datos (firma del asesor)."
---

# Bitácora | Mejoras en la App Evaluadora
## 2026-04-22 - Resumen de mejoras funcionales (M2 AI2)

**Files**: `file_processor.py`, `evaluator.py`, `analysis_engine.py`, `feedback_generator.py`, `app.py`  
**Tags**: #streamlit #evaluacion #ocr #transcripcion #segmentacion #ia #gemini  
**Objective**: Consolidar la extracción de entregas, métricas, rúbrica M2 AI2 y retroalimentación estructurada con IA; mejorar la UX del asesor con segmentación y export.  
**Segment**: App Development / Backend / Linguistic Analysis  

### Descripción del Proceso

Se implementó un conjunto de mejoras orientadas a la precisión de la evaluación y la robustez del visor de documentos. Los cambios principales incluyen:

1.  **Limpieza de JSON**: Eliminación de datos duplicados y consolidación de errores ortográficos y gramaticales.
2.  **Persistencia de Firma**: Integración de un campo de firma del asesor en el sidebar.
3.  **Detección de Colores**: Soporte para colores de fuente (`font color`) y sombreados complejos (`shading`) mediante la lectura directa de XML en Word y dibujo de rectángulos en PDF.
4.  **Visor PDF Granular**: Refactorización del visor para detectar resaltados palabra por palabra.
5.  **Flexibilidad Lingüística**: Inclusión de pronombres como sustantivos y participios como verbos.

---

## 🔄 Proceso de Validación Técnica

Se realizaron pruebas de integración automáticas en el contenedor Docker para verificar la exportación de JSON y la carga de módulos:

### Validación de Evaluator y Firma
```bash
docker exec 20260318_m02s1ai2_app_evaluador-evaluador_app-1 python3 -c "
import sys; sys.path.append('/app')
from file_processor import hex_to_category, rgb_to_category
from evaluator import Evaluator
e = Evaluator()
# Validar exportación con firma del asesor
fake_results = {'cognitivo': {'level_global': 'Experto', 'score': 100}, 'actitudinal': {'score': 100}, 'comunicativo': {'score': 100}, 'pensamiento_critico': {'score': 100}, 'total_score': 100}
extra = {'student_name': 'Garcia Lopez', 'firma_asesor': 'Asesor Virtual Test', 'highlights_detail': []}
out = e.export(fake_results, 'json', extra=extra)
import json; parsed = json.loads(out)
assert 'firma_asesor' in parsed, 'firma_asesor missing'
print('evaluator JSON export OK')
"
```

### Verificación de Sintaxis de App
```bash
docker exec 20260318_m02s1ai2_app_evaluador-evaluador_app-1 python3 -c "
import ast
with open('/app/app.py', 'r', encoding='utf-8') as f:
    ast.parse(f.read())
print('app.py syntax OK')
"
```

---


### ✅ Cambios implementados

**1. JSON sin duplicados**
- Eliminados `extra["recommendations"]`, `extra["suggestions"]` y la copia redundante de highlights dentro de `segments`.
- Los errores ortográficos viven únicamente en `orthography_matches` (top-level).
- Las palabras clasificadas viven únicamente en `highlights_detail`.

**2. Campo de firma del asesor**
- Nuevo `st.text_area` multilínea en la sección de Export (aparece antes del botón "Descargar JSON").
- La firma se guarda en `st.session_state["firma_asesor"]` y se incluye en el JSON bajo la clave `firma_asesor`.

**3. JSON exportado con nombre del estudiante**
- El archivo se descarga ahora con el nombre `evaluacion_<Nombre_Apellido>_M02AI2.json` (ej. `evaluacion_Garcia_Lopez_M02AI2.json`), construido automáticamente desde el nombre detectado en el archivo.

**4. Detección de color de letra (font color)**
- Se agregó una nueva función `_get_run_color_info(run)` que detecta en orden de prioridad:
  1. Color de resalte (`highlight_color`)
  2. Sombreado (`shading fill`)
  3. **Color de fuente** (`run.font.color.rgb`) ← nuevo
- En la vista previa HTML, las palabras marcadas con color de fuente se muestran con **subrayado del color** y texto en negrita (a diferencia del fondo de color usado para resaltados convencionales).


---
# Mejora en la deteccion de colores
El problema tiene dos causas. Voy a leer el código actual de `file_processor.py` para diagnosticar exactamente:

Viewed file_processor.py:22-155

Ya identifico los **dos problemas exactos**:

1. **`fc.rgb` lanza `TypeError` para colores de tema** — Word guarda la mayoría de los colores del panel de colores como *Theme Colors* (`MSO_COLOR_TYPE.THEME`), y `fc.rgb` lanza excepción silenciosa en esos casos. Hay que leer el atributo `w:val` directamente del XML.
2. **`hex_to_category` no tiene los códigos del panel de fuentes de Word** — el panel de "colores de fuente" usa códigos distintos (ej. verde = `70AD47`, azul = `4472C4`, rojo = `FF0000`). Solo amarillo (`FFFF00`) y gris (`A6A6A6`) coinciden por casualidad.

Edited file_processor.py

Ahora verifico en Docker:

Ran command: `docker exec 20260318_m02s1ai2_app_evaluador-evaluador_app-1 python3 -c "
import sys; sys.path.append('/app')
from file_processor import hex_to_category, rgb_to_category

# Test colores de fuente del panel de Word por categoria
tests = [
    # (hex, expected_category, descripcion)
    ('70AD47', 'VERB',  'Verde Office theme - VERB'),
    ('548235', 'VERB',  'Verde oscuro Office - VERB'),
    ('00FF00', 'VERB',  'Verde puro - VERB'),
    ('4472C4', 'NOUN',  'Azul Office theme - NOUN'),
    ('2E75B6', 'NOUN',  'Azul Office 2 - NOUN'),
    ('0000FF', 'NOUN',  'Azul puro - NOUN'),
    ('ED7D31', 'ADJ',   'Naranja Office - ADJ'),
    ('FFC000', 'ADJ',   'Amarillo Office - ADJ'),
    ('FFFF00', 'ADJ',   'Amarillo puro - ADJ'),
    ('FF0000', 'ADV',   'Rojo standard - ADV'),
    ('C00000', 'ADV',   'Rojo oscuro - ADV'),
    ('FF1493', 'ADV',   'Rosa intenso - ADV'),
    ('FF69B4', 'ADV',   'Rosa - ADV'),
    ('A6A6A6', 'DET',   'Gris medio - DET'),
    ('595959', 'DET',   'Gris oscuro - DET'),
    ('7030A0', 'ADP',   'Morado Office - ADP'),
    ('9C27B0', 'ADP',   'Morado Material - ADP'),
    ('5C2D91', 'ADP',   'Morado oscuro - ADP'),
]

ok, fail = 0, 0
for (h, expected, desc) in tests:
    result = hex_to_category(h)
    if result == expected:
        print(f'  OK  {desc}: {h} -> {result}')
        ok += 1
    else:
        print(f'  FAIL {desc}: {h} -> {result} (expected {expected})')
        fail += 1

print(f'\nResultado: {ok}/{ok+fail} correctos')
"
`

**18/18 correctos.** Ahora ya no tendrás que reiniciar Docker porque los archivos Python se recargan en cada ejecución — basta con hacer una nueva evaluación. 

### Diagnóstico y solución aplicada

**Causa raíz:** Había **dos problemas combinados**:

1. **`fc.rgb` lanza `TypeError` en colores de tema** — Word guarda la mayoría de los colores del panel como *Theme Colors*, y `fc.rgb` falla silenciosamente para ellos. Lo corregí leyendo el atributo `w:val` directamente del XML, que siempre contiene el color hexadecimal resuelto sin importar si es RGB o de tema.

2. **Paleta de `hex_to_category` incompleta** — Los colores del panel de "Color de fuente" de Word son distintos a los del panel de "Resaltado":
   - Resaltado verde: `92D050` ← estaba
   - Fuente verde Office: `70AD47` ← **faltaba**
   - Fuente azul Office: `4472C4` ← **faltaba**
   - Fuente rojo: `FF0000`, `C00000` ← **faltaban**
   - Etc.

Se agregaron ~40 códigos adicionales para los 6 colores del panel de fuentes de Word (Office 365 / 2019 / 2016), más se amplió el umbral de similitud fuzzy de `0.35` → `0.42` para cubrir variaciones menores.

---

## 🚀 Actualización: Mejoras de Precisión y Visualización (Documentos M2 AI2)

**Fecha**: 2026-04-22 (Sesión tarde)
**Files**: `file_processor.py`, `analysis_engine.py`

### 1. Detección de Colores "Pastel" y Google Docs
- **Problema**: Alumnos usando temas claros de Word o exportaciones de Google Docs tenían colores (ej. rosa `EAD1DC`, azul `C9DAF8`) que no se detectaban por ser pasteles.
- **Solución**: Se agregaron ~12 códigos HEX de la paleta "Pastel/Light" y se incluyeron como anclas RGB para el motor fuzzy. Ahora la detección es mucho más robusta ante variaciones de tono.

### 2. Vista Previa de PDF Granular (Palabra por palabra)
- **Problema**: En PDFs con bloques de texto masivos, el resaltado de una sola palabra se "ahogaba" en el bloque y no se mostraba en la vista previa del visor.
- **Solución**: Se refactorizó `_build_html_from_pdf` para analizar cada palabra individualmente. Ahora el visor es capaz de pintar resaltados precisos palabra por palabra, igualando lo que se ve en la tabla de evaluación.

### 3. Flexibilidad Gramatical Pedagógica
- **Pronombres como Sustantivos**: "Ella", "Él", etc., ahora se validan como correctos bajo la etiqueta **Sustantivo** (NOUN), atendiendo a la simplificación pedagógica de la rúbrica.
- **Participios como Verbos**: Terminaciones "-ado/-ido" (ej: "programada") se aceptan como **Verbos** (VERB).
- **Filtro de Números**: Se omiten los números (ej: "8") del cálculo de precisión si fueron resaltados por error.

### 4. Firma del Asesor
- Movida al **sidebar izquierdo** para mayor visibilidad y persistencia durante la sesión. Se incluye automáticamente en el JSON final.

---
**Resultado**: Aplicación verificada con archivos `LojeroSalazar_Estrella_M02S1AI2.pdf`, `CancholaGomez_Alisson_M02S1AI2.docx` y `TENA_VILLAFAÑE_EUNICE_ABIGAIL_M02S1AI2.docx`. Se ha logrado una cobertura completa de paletas pastel y vibrantes. Adicionalmente, se han integrado los colores vibrantes `FF66FF` y `9966FF` a la paleta de detección.