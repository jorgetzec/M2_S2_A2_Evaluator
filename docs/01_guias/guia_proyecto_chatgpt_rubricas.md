# Guía de Proyecto: Generación de Rúbricas Humanizadas

Esta guía establece las directrices para el uso de modelos de lenguaje (IA) en la creación y el procesamiento de rúbricas de evaluación dentro del ecosistema del proyecto Evaluador. El objetivo es asegurar que cada rúbrica generada mantenga un estándar de calidad, empatía y estructura técnica compatible con nuestra aplicación.

---

## 1. Filosofía y Tono
Nuestras rúbricas no son solo instrumentos de medición; son herramientas de acompañamiento pedagógico. 

- **Empatía ante todo:** Las descripciones de los niveles inferiores (Aprendiz, Requiere Apoyo) deben centrarse en lo que el estudiante *necesita alcanzar* o en lo que *se observa ausente*, evitando términos punitivos.
- **Claridad técnica:** Cada nivel debe ser autoexplicativo y cuantificable (ej. "identifica el 90% de...", "cumple con 10 de 12 indicaciones") e indicar algunos ejemplos de esos errores y como mejorarlos.
- **Tono constructivo:** Incluso en el nivel "No Evaluable", el lenguaje debe invitar a la reorientación y al contacto con el asesor.
- **Lenguaje Cualitativo:** Evitar mencionar puntajes o calificaciones numéricas. Es preferible usar descriptores generales como "mucho", "poco", "algunos", "varios", "gran parte de", etc.

---

## 2. Estructura Obligatoria de la Rúbrica
Para garantizar la compatibilidad con el motor de análisis y el generador de retroalimentación, toda rúbrica debe seguir este esquema basado en el modelo de Prepa en Línea-SEP:

### A. Dominios de Evaluación
1.  **Cognitivo:** Evalúa el "saber hacer" y los productos entregados (relatos, audios, análisis).
2.  **Actitudinal:** Evalúa el cumplimiento de instrucciones, el uso de la tecnología y la puntualidad. Solo se mide por porcentaje de cumplimiento (100% para Experto).
3.  **Comunicativo:** Evalúa la claridad del mensaje, la netiqueta y la precisión gramatical/ortográfica.
4.  **Pensamiento Crítico:** Evalúa la profundidad del análisis, la capacidad de síntesis y la comprensión de fondo de los conceptos.

### B. Niveles de Desempeño y Puntajes
- **Experto (100 pts):** Dominio total de la competencia.
- **Capacitado (90 pts):** Cumple con lo solicitado, con omisiones menores o imprecisiones leves.
- **Aceptable (80 pts):** Logra el propósito general, pero presenta áreas de oportunidad claras en calidad o extensión.
- **Aprendiz (70 pts):** Requiere fortalecer aspectos básicos para alcanzar el estándar.
- **Requiere Apoyo (60 pts):** El desempeño es insuficiente y pone en riesgo el aprendizaje.
- **No Evaluable (0 pts):** Plagio total, entrega incorrecta o incapacidad de valoración.

### C. El Factor de Originalidad (Deducciones)
A diferencia de los dominios anteriores, la **Originalidad** se aplica como una deducción negativa al puntaje total:
- **Bien:** -25 puntos (algunos indicios de falta de originalidad).
- **Regular:** -50 puntos.
- **Suficiente:** -75 puntos.
- **Insuficiente:** -100 puntos.

---

## 3. Uso del JSON para Generación Rápida
El proyecto utiliza un formato JSON serializado para definir los criterios. Al alimentar la IA con este JSON, el modelo debe ser capaz de expandirlo en una rúbrica completa en Markdown.

### Estructura de Entrada sugerida (Input JSON):
```json
{
  "actividad_id": "M2_AI2",
  "titulo": "Mi Historia de Vida",
  "criterios_base": [
    {
      "nombre": "Cognitivo",
      "requerimientos": [
        "Relato en Arial 12 (1-2 cuartillas)",
        "Identificación de 6 clases de palabras por colores",
        "Grabación de audio/video 2-3 min",
        "Párrafo de diferencias oral/escrito (5-10 líneas)"
      ]
    },
    {
      "nombre": "Actitudinal",
      "puntos_clave": ["Sigue 12 instrucciones tecnológicas y de formato"]
    }
  ]
}
```

### Comportamiento esperado de la IA en la generación de la rúbrica:
1.  **Interpretación:** La IA lee los requerimientos y genera las descripciones detalladas para cada uno de los 5 niveles (Experto a Requiere Apoyo).
2.  **Mapeo de Errores:** En el criterio Comunicativo, debe respetar los rangos estándar de errores ortográficos:
    - Experto: 0 errores.
    - Capacitado: 1-3 errores.
    - Aceptable: 4-5 errores.
    - Aprendiz: 6-8 errores.
    - Requiere Apoyo: >8 errores.
3.  **Generación de Tablas:** El formato de salida debe ser siempre **Markdown GFM (GitHub Flavored Markdown)** con tablas limpias y bien alineadas.
4.  **Ejemplos de Errores:** Al describir niveles de bajo desempeño, la IA debe incluir ejemplos genéricos de lo que el estudiante podría estar fallando (ej. "olvido de acentos en palabras agudas" o "confusión entre preposiciones y artículos").

---

## 4. Guía de Retroalimentación (Escritura en Prosa)
Además de la rúbrica, la IA debe generar una retroalimentación personalizada siguiendo esta estructura de 13 bloques obligatorios:

1.  **Saludo:** "Hola [Nombre]:"
2.  **Apertura:** Conexión con objetivos, reconocimiento general y netiqueta.
3.  **Ejercicio 1 (Relato):** Feedback sobre extensión, formato y contenido.
4.  **Ejercicio 2 (Clases de palabras):** Feedback sobre identificación y colores.
5.  **Ejercicio 3 (Audio/video):** Feedback sobre liga, duración y naturalidad.
6.  **Ejercicio 4 (Párrafo oral/escrito):** Feedback sobre el análisis de diferencias.
7.  **Cumplimiento técnico:** Nombre de archivo, envío y puntualidad.
8.  **Criterio comunicativo:** Organización, ortografía y puntuación.
9.  **Pensamiento crítico:** Comprensión de fondo y capacidad de análisis.
10. **Originalidad:** Solo si hubo deducción (mencionar de forma constructiva).
11. **Recurso sugerido:** Enlace de apoyo específico al área de mejora.
12. **Cierre:** Pregunta reflexiva o mensaje de ánimo.
13. **Despedida:** "Saludos," + firma del asesor.

### Directrices de Redacción de Feedback:
- **Cero números:** No mencionar "sacaste 80" o "perdiste 5 puntos".
- **Foco en el proceso:** Decir "lograste capturar gran parte de tu historia" en lugar de "cumples con el 80% del contenido".
- **Uso de Indefinidos:** Utilizar palabras como "algunos errores", "varias áreas de oportunidad", "se observa poco detalle en...", "noto mucho entusiasmo en...".
- **Ejemplificación:** Al mencionar faltas ortográficas, citar ejemplos encontrados en el texto: "noté algunas omisiones en acentos, como en las palabras 'paso' por 'pasó'".

---

## 4. Ejemplos de Referencia
Para mantener la consistencia, consulte los siguientes documentos en la carpeta `docs`:
- `03_data_AI2/m2_ai2_rubrica.md`: Estructura visual y descriptiva.
- `03_data_AI2/m2_ai2_retroalimentacion.md`: Mapeo de cómo cada nivel de la rúbrica se traduce en frases de apoyo.

---

## 5. Manejo de Discrepancias Técnicas (Clasificación de Palabras)
El sistema automático puede presentar errores en la detección de categorías gramaticales debido a la ambigüedad del lenguaje. La IA debe actuar como un filtro de calidad final.

### Validación de Categorías
Las categorías obligatorias y sus colores asociados (para referencia en la retroalimentación) son:
- **Verbos:** Verde
- **Sustantivos:** Azul
- **Adjetivos:** Amarillo
- **Adverbios:** Rosa
- **Artículos:** Gris
- **Preposiciones:** Morado

### Corrección en la Retroalimentación
Si el JSON de entrada contiene una lista de palabras evaluadas (`highlights_detail`) y detectas que el sistema ha clasificado erróneamente una palabra:
- **Prioriza tu conocimiento lingüístico:** No repitas el error del sistema en la retroalimentación.
- **Versión Corregida:** Si el sistema marca como "error" una palabra que el estudiante clasificó correctamente (o viceversa por una falla del algoritmo), ajusta tu comentario para reflejar la realidad gramatical.
- **No evidenciar fallas del sistema:** Evita frases como "el sistema se equivocó". Simplemente redacta la retroalimentación de forma que sea pedagógicamente correcta, ignorando los falsos positivos o negativos del JSON.

---

## 6. Recomendaciones Finales
- **No inventar métricas:** Si el JSON especifica "2-3 minutos de audio", no permitir variaciones en el nivel Experto.
- **Personalización:** Asegurarse de que el nombre del asesor y el contexto de la actividad aparezcan en el encabezado generado.
- **Revisión de Sensibilidad:** Antes de entregar la rúbrica o retroalimentación, verificar que el lenguaje utilizado no sea agresivo y fomente la perseverancia del estudiante. 
