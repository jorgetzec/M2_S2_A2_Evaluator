# Sistema de Retroalimentación M2 AI2 - Mi Historia de Vida

Documento para generar retroalimentación automatizada con Ollama u otros modelos pequeños. Incluye prompt del sistema, estructura obligatoria y mapeo de métricas a frases.

---

## 1. System Prompt (para Ollama)

```
Eres un asesor virtual de Prepa en Línea-SEP. Tu tarea es redactar una retroalimentación personalizada para la actividad "Mi Historia de Vida" (M2 AI2).

INSTRUCCIONES:
- Usa un tono cercano, respetuoso y constructivo. Trata al estudiante por su nombre.
- Reconoce siempre el esfuerzo realizado, incluso cuando haya áreas de mejora.
- No uses lenguaje punitivo ni desalentador.
- Las sugerencias deben ser concretas y accionables.
- La extensión total debe ser similar al ejemplo de referencia (aproximadamente 400-600 palabras).
- Escribe en español de México.
- Sigue EXACTAMENTE la estructura indicada en las secciones 2 y 3.
- Usa los datos de evaluación que te proporcione para generar frases específicas, no genéricas.
```

---

## 2. Estructura obligatoria de la retroalimentación

La retroalimentación debe seguir este orden. Cada bloque corresponde a un criterio o ejercicio.

| Orden | Bloque | Contenido |
| :---: | :--- | :--- |
| 1 | **Saludo** | "Hola [Nombre]:" |
| 2 | **Apertura** | Conexión con objetivos de aprendizaje, reconocimiento general, netiqueta si aplica |
| 3 | **Ejercicio 1 – Relato** | Feedback sobre relato escrito (extensión, formato, contenido) |
| 4 | **Ejercicio 2 – Clases de palabras** | Feedback sobre identificación y colorización |
| 5 | **Ejercicio 3 – Audio/video** | Feedback sobre grabación, liga, duración, naturalidad |
| 6 | **Ejercicio 4 – Párrafo oral/escrito** | Feedback sobre el análisis de diferencias |
| 7 | **Cumplimiento técnico** | Nombre de archivo, envío, tiempo de entrega |
| 8 | **Criterio comunicativo** | Organización, ortografía, puntuación |
| 9 | **Pensamiento crítico** | Identificación de diferencias, comprensión de clases de palabras |
| 10 | **Originalidad** | Solo si hubo deducción; mencionar de forma constructiva |
| 11 | **Recurso sugerido** | Enlace de apoyo según áreas de mejora |
| 12 | **Cierre** | Pregunta reflexiva opcional, ánimo, disposición para dudas |
| 13 | **Despedida** | "Saludos," + firma del asesor |

---

## 3. Mapeo: métricas → frases de retroalimentación

Usar estos fragmentos según el resultado de cada métrica. Combinar o adaptar para que suenen naturales.

### 3.1 Relato escrito (Cognitivo)

| Métrica | Resultado | Frase sugerida |
| :--- | :--- | :--- |
| Extensión | Cumple 1-2 cuartillas | "tu relato se ha apegado al formato y la extensión solicitados" |
| Extensión | Muy corto (&lt;250 palabras) | "tu relato es breve; te sugiero ampliarlo a una extensión mínima de una cuartilla para desarrollar mejor tu historia" |
| Extensión | Muy largo (&gt;600 palabras) | "tu relato excede la extensión solicitada; considera condensar a máximo dos cuartillas para mantener el enfoque" |
| Fuente | Arial 12 pt | "has utilizado el formato de fuente solicitado" |
| Fuente | Diferente | "recuerda usar fuente Arial de 12 puntos en futuros documentos" |
| Título | Correcto | "has incluido el título solicitado" |
| Título | Omite/incorrecto | "no olvides titular tu relato como 'El relato de mi historia'" |
| Contenido | Rico en detalles | "tu relato incluye descripciones detalladas que enriquecen la narrativa" |
| Contenido | Mejorable | "para futuros relatos, considera el uso de descripciones detalladas y diálogos que hagan tu historia más envolvente" |

### 3.2 Clases de palabras

| % aciertos | Frase sugerida |
| :---: | :--- |
| 100% | "has identificado correctamente todas las clases de palabras (verbos, sustantivos, adjetivos, adverbios, artículos y preposiciones)" |
| ≥90% | "has identificado correctamente la mayoría de las clases de palabras; revisa los casos en los que hubo confusión" |
| ≥80% | "identificaste gran parte de las clases de palabras; te sugiero repasar adverbios y preposiciones para afianzar su reconocimiento" |
| ≥70% | "hay varias palabras sin clasificar correctamente; sería útil revisar el material sobre clases de palabras antes de la siguiente actividad" |
| ≥60% | "es importante que repases verbos, sustantivos, adjetivos, adverbios, artículos y preposiciones; son la base para comprender la estructura del lenguaje" |
| &lt;60% o ausente | "no se observa la identificación de clases de palabras con colores; este ejercicio es fundamental para la unidad, te invito a realizarlo" |

**Recordatorio de colores:** verbos verde, sustantivos azul, adjetivos amarillo, adverbios rosa, artículos gris, preposiciones morado.

### 3.3 Audio o video

| Situación | Frase sugerida |
| :--- | :--- |
| Liga presente, 2-3 min, buena calidad | "grabaste un relato de tu vida con la duración solicitada y compartiste correctamente la liga; la calidad del audio/video permite apreciar tu narración" |
| Liga presente, duración incorrecta | "compartiste la liga correctamente; la próxima vez procura que el relato tenga entre 2 y 3 minutos" |
| Liga no presente o no funcional | "no encontré la liga de acceso al audio/video, o no está funcionando; recuerda incluirla al final del documento y verificar que sea accesible" |
| No hay grabación | "no se encontró la grabación de tu relato oral; esta parte es esencial para identificar las diferencias entre comunicación escrita y oral" |
| Leyó en lugar de narrar | "noté que leíste el texto en lugar de narrarlo de forma natural. Es importante realizar el relato sin leerlo, para experimentar las diferencias entre lo escrito y lo oral. Te sugiero hacer un esquema y practicar varias veces" |
| Narración natural | "narraste tu historia de manera fluida y natural, lo que permite apreciar bien las diferencias con la expresión escrita" |
| Calidad baja pero comprensible | "la calidad del audio/video dificulta un poco la comprensión; para futuras grabaciones, procura un entorno con menos ruido" |

### 3.4 Párrafo oral vs escrito

| Situación | Frase sugerida |
| :--- | :--- |
| Presente, 5-10 líneas, buenas diferencias | "escribiste un párrafo con la extensión solicitada sobre las diferencias entre la expresión oral y escrita. Las diferencias que mencionas son acertadas y demuestran reflexión" |
| Presente, extensión incorrecta | "incluiste el párrafo sobre las diferencias; te sugiero ajustar la extensión a entre 5 y 10 líneas para desarrollar mejor tu análisis" |
| Presente, diferencias poco claras | "el párrafo sobre las diferencias está presente; sería útil que profundices en aspectos concretos (por ejemplo: espontaneidad, corrección, planificación)" |
| Ausente | "no encontré el párrafo sobre las diferencias entre expresión oral y escrita; este análisis es importante para los objetivos de la unidad" |
| Sin oralidad para comparar | "al no contar con la grabación, no fue posible valorar si identificaste las diferencias entre ambos tipos de comunicación" |

### 3.5 Cumplimiento técnico (Actitudinal)

| Indicación | Cumple | No cumple |
| :--- | :--- | :--- |
| Nombre de archivo | "enviaste correctamente el archivo y lo nombraste como se solicita (Apellidos_Nombre_M02S1AI2)" | "el nombre del archivo no coincide con el formato solicitado; recuerda usar Apellidos_Nombre_M02S1AI2" |
| Envío en plataforma | "enviaste el archivo en el espacio destinado" | "verifica que hayas subido el archivo al espacio correcto de la plataforma" |
| Tiempo de entrega | "entregaste en el tiempo establecido" | "la entrega fue fuera del plazo; te sugiero organizar tus tiempos para futuras actividades" |
| Resumen cumplimiento | "sigues la mayoría de las indicaciones" / "sigues todas las indicaciones" | "algunas indicaciones no fueron atendidas; revisa la guía de la actividad para la próxima ocasión" |

### 3.6 Criterio comunicativo

| Métrica | Resultado | Frase sugerida |
| :--- | :--- | :--- |
| Organización | Clara y coherente | "organizas la información de manera clara, coherente y precisa" |
| Organización | Poco clara | "la organización del texto podría mejorar; procura seguir un hilo lógico entre las ideas" |
| Organización | Confusa | "la organización dificulta la comprensión; te sugiero hacer un esquema previo antes de escribir" |
| Ortografía | 0 errores | "no presentas errores en sintaxis, ortografía o puntuación" |
| Ortografía | 1-3 errores | "hay algunos errores menores de ortografía o puntuación; puedes usar LenguageTool: https://youtu.be/Zg4Ua3G8wkU" |
| Ortografía | 4-8 errores | "se observan varios errores de ortografía y puntuación; te recomiendo revisar con un corrector como LenguageTool antes de entregar" |
| Ortografía | &gt;8 errores | "hay numerosos errores ortográficos; es importante que revises tus escritos con ayuda de LenguageTool: https://youtu.be/Zg4Ua3G8wkU" |
| Netiqueta | Cumple | "sigues las normas de netiqueta para la comunicación en entornos virtuales" |
| Netiqueta | No cumple | "recuerda mantener un lenguaje respetuoso y adecuado en los entornos virtuales de aprendizaje" |

### 3.7 Pensamiento crítico

| Situación | Frase sugerida |
| :--- | :--- |
| Identifica bien las diferencias | "demuestras una buena comprensión de las diferencias entre comunicación oral y escrita" |
| Identifica con dificultad | "identificas algunas diferencias; sería útil profundizar más en cómo la planificación, la espontaneidad y la corrección cambian entre lo oral y lo escrito" |
| No identifica o hay errores | "el análisis de las diferencias entre oral y escrito requiere mayor desarrollo; te sugiero revisar el material y participar en el foro para ver otros ejemplos" |
| Clases de palabras bien comprendidas | "tu identificación de clases de palabras demuestra que comprendes su clasificación y función" |
| Clases de palabras con dudas | "sería útil repasar la clasificación de verbos, sustantivos, adjetivos, adverbios, artículos y preposiciones; el recurso que te comparto puede ayudarte" |

### 3.8 Originalidad (solo si hay deducción)

| Nivel deducción | Frase sugerida (constructiva, sin acusar) |
| :--- | :--- |
| Bien (-25) | "en algunos apartados el texto podría reflejar más tu voz personal; te invito a incorporar anécdotas y detalles que te sean propios" |
| Regular (-50) | "es importante que el relato surja de tu propia experiencia; incluir nombres, lugares y momentos concretos ayudará a que sea más auténtico" |
| Suficiente (-75) | "el relato parece poco personal; recuerda que la actividad pide tu historia de vida, con tus experiencias y tu forma de expresarte" |
| Insuficiente (-100) | "la actividad solicita un relato personal y original; si hay dudas sobre cómo desarrollarlo, puedes consultarme o revisar los recursos de la unidad" |

**Nota:** No mencionar explícitamente "IA" o "plagio" en la retroalimentación. Usar frases que inviten a la originalidad y al desarrollo de ideas propias.

---

## 4. Recursos sugeridos

Incluir según las áreas de mejora detectadas. Fuentes: RAE, SEP, UNAM, INTEF y herramientas ampliamente usadas.

### Por área de mejora

| Área | Recurso | Fuente |
| :--- | :--- | :--- |
| **Clases de palabras** | [Clases de palabras (CCH-UNAM)](https://e1.portalacademico.cch.unam.mx/alumno/tlriid2/unidad1/catGramaticales/clasesDePalabras1) | UNAM |
| **Clases de palabras** | [Clases y subclases de palabras – Nueva gramática básica](https://www.rae.es/gramatica-basica/determinantes-y-pronombres/clases-y-subclases-de-palabras) | RAE |
| **Clases de palabras** | [Unidades sintácticas: clases de palabras](https://www.rae.es/gramatica/cuestiones-generales/unidades-sintacticas-i-clases-de-palabras-criterios-de-clasificacion) | RAE |
| **Ortografía** | [LenguageTool – Tutorial](https://youtu.be/Zg4Ua3G8wkU) | YouTube |
| **Ortografía** | [LanguageTool corrector en línea](https://languagetool.org/es/corrector-ortografico-espanol) | LanguageTool |
| **Ortografía** | [Signos de puntuación – Ortografía RAE](https://www.rae.es/ortografia/signos-de-puntuacion) | RAE |
| **Ortografía** | [Diccionario de la lengua española (DLE)](https://dle.rae.es/) | RAE |
| **Ortografía** | [Scribens corrector](https://www.scribens.com/es/) – ortografía y gramática en español | Scribens |
| **Comunicación oral vs escrita** | [De lo oral a lo escrito](https://nuevaescuelamexicana.sep.gob.mx/contenido/coleccion/de-lo-oral-a-lo-escrito/) | SEP – Nueva Escuela Mexicana |
| **Comunicación oral vs escrita** | [AprendeEnCasa – Narramos en forma escrita](https://www.youtube.com/watch?v=KtY5Gy77Ck8) | SEP – YouTube |
| **Redacción / relato narrativo** | [Redacto, reviso y corrijo mi cuento](https://nuevaescuelamexicana.sep.gob.mx/contenido/coleccion/redacto-reviso-y-corrijo-mi-cuento-2/) | SEP – Nueva Escuela Mexicana |
| **Redacción / relato narrativo** | [Las partes de la narración](https://descargas.intef.es/recursos_educativos/It_didac/Leng_Pri/2/10/02_Partes_narracion/las_partes_de_la_narracin.html) | INTEF |
| **Netiqueta** | [10 normas de netiqueta para entornos virtuales](https://edu-labs.co/articulos/10-normas-de-netiqueta-para-entornos-virtuales-de-aprendizaje/) | Edu-labs |
| **Netiqueta** | [Normas del foro: netiqueta](https://formacion.intef.es/aulaenabierto/mod/book/view.php?id=3752&chapterid=4954) | INTEF – Aula en Abierto |
| **General / Pensamiento crítico** | Participación en foro aprendiendo y espacios abiertos | Prepa en Línea-SEP |

---

## 5. Formato de entrada (para el modelo)

Estructura JSON sugerida con los datos de evaluación para que el modelo genere la retroalimentación:

```json
{
  "estudiante": {
    "nombre": "Sherlyn",
    "apellidos": "Rodríguez Baca"
  },
  "evaluacion": {
    "cognitivo": {
      "relato_extension": "cumple",
      "relato_fuente": "cumple",
      "relato_titulo": "cumple",
      "clases_palabras_porcentaje": 100,
      "audio_presente": true,
      "audio_liga_funcional": true,
      "audio_duracion_min": 2.5,
      "parrafo_oral_escrito_presente": true,
      "parrafo_oral_escrito_lineas": 7
    },
    "actitudinal": {
      "indicaciones_cumplidas": 12,
      "indicaciones_totales": 12,
      "nombre_archivo_correcto": true,
      "envio_plataforma": true,
      "tiempo_entrega": "a_tiempo"
    },
    "comunicativo": {
      "organizacion": "clara",
      "errores_ortografia": 0,
      "netiqueta": "cumple",
      "audio_calidad": "alta",
      "audio_leyo_o_narrote": "leyo"
    },
    "pensamiento_critico": {
      "identifica_diferencias": true,
      "coherencia_analisis": "buena",
      "comprende_clases_palabras": true
    },
    "originalidad": {
      "deduccion_puntos": 0,
      "nivel": "excelente"
    }
  },
  "curso": "M2C1G82-021",
  "asesor": {
    "nombre": "Ricardo Raúl Estrada Pérez"
  }
}
```

---

## 6. Ejemplo completo de referencia

```
Hola Sherlyn:

Espero que esta actividad te haya ayudado a recordar las clases de palabras y a diferenciar entre la comunicación escrita y la oral. Identificar verbos, sustantivos, adjetivos, adverbios, artículos y preposiciones es muy útil en la vida cotidiana, ya que mejora tu capacidad de comprender y utilizar el lenguaje de manera efectiva. Además, distinguir entre la comunicación escrita y oral te permitirá comunicarte de manera más adecuada en distintas situaciones. Has demostrado un buen nivel de comprensión, pero con un poco más de esfuerzo, podrías profundizar aún más en estos temas y mejorar tu desempeño. Reconozco tu esfuerzo en realizar la actividad y en seguir las normas de netiqueta para la comunicación en entornos virtuales de aprendizaje.

En el primer ejercicio, tu relato sobre la historia de tu vida ha sido interesante y se ha apegado al formato y la extensión solicitados. Para futuros relatos, sería útil que consideres el uso de descripciones detalladas y diálogos que enriquezcan la narrativa. Esto hará que tus historias sean aún más envolventes y vividas para el lector.

En el ejercicio 2, has demostrado una buena capacidad para identificar correctamente todas las clases de palabras. Este conocimiento es fundamental porque te permite comprender mejor cómo se estructura el lenguaje y cómo cada parte contribuye al significado de una oración. 

Para el ejercicio 3, grabaste un relato de tu vida. Sin embargo, noté que lo leíste en lugar de narrarlo de forma natural. Es importante realizar el relato sin leerlo, ya que esto te permite experimentar las diferencias entre la elaboración de un relato escrito y uno oral. Te sugiero que hagas un esquema y practiques varias veces para sentirte más cómodo con el contenido.

En el ejercicio final, escribiste un párrafo con la extensión solicitada sobre las diferencias entre la expresión oral y escrita. Las diferencias que mencionas son interesantes. Aunque se te da muy bien la expresión escrita, no olvides seguir trabajando en la expresión oral para fortalecer aún más tus habilidades en ambas áreas.

Por otro lado, puedo ver que has empleado la tecnología para generar tu documento con toda la información solicitada, siguiendo todas las instrucciones para la elaboración de la actividad. Enviaste correctamente el archivo en el espacio destinado y lo has nombrado como se solicita en las instrucciones. Has entregado en el tiempo establecido tu documento, sin algún retraso.

En cuanto al criterio comunicativo, organizas toda la información de manera clara, coherente y precisa. No presentas errores en sintaxis, ortografía o puntuación, y presentas las ideas de manera lógica y congruente. Recuerda que siempre puedes utilizar revisores de ortografía como LenguageTool para revisar tus escritos. Te dejo un tutorial para que veas cómo utilizarlo: https://youtu.be/Zg4Ua3G8wkU.

Respecto al criterio de Pensamiento Crítico, tu trabajo muestra un buen inicio en la identificación de las diferencias entre la comunicación oral y escrita. Sería útil profundizar más en estos temas, así como en la clasificación de verbos, sustantivos, adjetivos, adverbios, artículos y preposiciones. Te sugiero revisar estos conceptos con mayor detenimiento y participar en el foro aprendiendo, así como en los espacios abiertos para ver diferentes perspectivas y aplicaciones prácticas. 

Después de haber visto este tema me parece que este recurso podría complementar lo que vimos. Te puede ayudar a profundizar en las categorías gramaticales, y cómo las puedes manejar de la mejora manera. Te recomiendo revisarlo: 
https://e1.portalacademico.cch.unam.mx/alumno/tlriid2/unidad1/catGramaticales/clasesDePalabras1

Como cierre, considerando lo aprendido en esta unidad, ¿cómo podrías conectar lo visto sobre comunicación oral y escrita con situaciones reales en tu vida diaria? Lo has hecho bien, reconozco tu esfuerzo y dedicación. El aprendizaje es continuo, cada paso cuenta en tu desarrollo académico, sigue adelante con determinación, tu dedicación es clave para alcanzar metas. Me despido reiterando mi reconocimiento por tu esfuerzo y poniéndome a tu disposición por si tuvieras alguna duda respecto a tu calificación o retroalimentación.

Saludos,

Ricardo Raúl Estrada Pérez
Asesor Virtual
M2C1G81-021.
```

### Otros ejemplos
Calificación: 66
```
Hola Irving:

Espero que esta actividad te haya permitido recordar las clases de palabras y analizar las diferencias entre la comunicación escrita y la oral. Identificar verbos, sustantivos, adjetivos, adverbios, artículos y preposiciones es muy útil en la vida cotidiana, ya que facilita una mejor comprensión y uso del lenguaje. Tuviste algunos desafíos, pero con un poco más de esfuerzo y enfoque, podrías mejorar notablemente tu comprensión de estos temas. Diferenciar entre la comunicación escrita y oral te permitirá comunicarte de manera más adecuada en diversas situaciones. Quiero reconocer tu esfuerzo en realizar la actividad y en seguir las normas de netiqueta en los entornos virtuales de aprendizaje.

En el primer ejercicio, tu relato sobre la historia de tu vida ha sido interesante, y presentas un buen desarrollo de ideas. Sería beneficioso que trabajes en profundizar tus argumentos, añadiendo más detalles y ejemplos específicos. También, recuerda seguir las instrucciones del formato y la extensión solicitada. Para desarrollar más tus ideas, puedes utilizar preguntas reflexivas que inviten al lector a pensar más sobre tu historia.

En el ejercicio 2, has mostrado iniciativa al identificar varias categorías gramaticales como verbos, sustantivos, adjetivos, adverbios, artículos y preposiciones. Sería recomendable revisar nuevamente estas categorías, ya que no todas las palabras fueron clasificadas correctamente. Dominar la gramática te proporcionará las herramientas necesarias para comunicarte de manera clara y persuasiva, mejorando así tus habilidades en debates, presentaciones y escritura.

Puedo ver que se te ha complicado realizar y compartir tu grabación. Espero este recurso te pueda ser útil para compartir tus audios y videos en futuras actividades: https://youtu.be/uZboUIr54Gw.

En el ejercicio final, puedo notar que se te ha complicado realizar el párrafo sobre las diferencias encontradas al expresarte de manera oral y escrita. Es importante realizar estos ejercicios, pues te permiten reflexionar sobre tus fortalezas y áreas de oportunidad. 

Por otro lado, puedo ver que has empleado la tecnología para generar tu documento con la información solicitada; sin embargo, dejaste de lado muchas de las instrucciones para la elaboración de la actividad. Te sugiero que revises detalladamente las instrucciones para las próximas actividades, de manera que puedas obtener un mejor puntaje. Si tienes dudas durante el proceso, no dudes en escribirme por el chat para resolverlas y participar en los espacios abiertos, lo cual te ayudará a realizar una buena actividad. Enviaste correctamente el archivo en el espacio destinado y lo has nombrado como se solicita en las instrucciones. Has entregado en el tiempo establecido tu documento, sin algún retraso.

En cuanto al criterio comunicativo, organizas toda la información de manera clara, coherente y precisa. Presentas algunas faltas de ortografía y sintaxis, por lo que antes de enviar tus actividades te recomiendo que utilices un revisor de ortografía como LanguageTool. Te dejo un tutorial para que veas cómo utilizarlo: https://youtu.be/Zg4Ua3G8wkU.

Para el criterio de pensamiento crítico, te recomendaría comenzar revisando los recursos proporcionados en el curso y las grabaciones de las sesiones de espacio abierto en vivo, para asegurarte de estar al día con el contenido. Es importante que retomes esta tarea para desarrollar tu habilidad de distinguir entre estos dos tipos de expresión y comprender cómo se estructura el lenguaje. 

Después de haber visto este tema me parece que este recurso podría complementar lo que vimos, resume en parte las clases de palabras y te ofrecen algunos ejercicios para seguir practicando su clasificación, te recomiendo revisarlo http://cea.cide.edu/gramtica/tipos_de_palabras.html.

Ya para finalizar, con base en lo que vimos sobre la comunicación oral y escrita ¿cómo crees que tu habilidad para distinguir entre la comunicación oral y escrita podría influir en tu desempeño académico y profesional? Ánimo, sé que alcanzar la meta en algunas ocasiones es cansado y desgastante, pero valdrá la pena. Sigue las sugerencias, analiza las instrucciones, entra los espacios abiertos y revisa las rúbricas de evaluación, verás que podrás obtener mejores puntajes. Las calificaciones no definen tu valía como estudiante, lo importante es tu compromiso y perseverancia al completar las actividades. Aprende de los desafíos y utiliza la retroalimentación para crecer y mejorar. Me despido reiterando mi reconocimiento por tu esfuerzo y poniéndome a tu disposición por si tuvieras alguna duda respecto a tu calificación o retroalimentación.
Saludos,

Ricardo Raúl Estrada Pérez
Asesor Virtual
M2C1G82-021.
```

Calificación:26
```
Hola Ricardo:

Espero que esta actividad te haya permitido recordar las clases de palabras y analizar las diferencias entre la comunicación escrita y la oral. Identificar verbos, sustantivos, adjetivos, adverbios, artículos y preposiciones es una ventaja en la vida cotidiana, ya que te permite utilizar el lenguaje de manera más efectiva y comprensible. Aunque encontraste algunos obstáculos, con más esfuerzo y dedicación, puedes mejorar significativamente tu comprensión y uso de estos conceptos. Diferenciar entre la comunicación escrita y la oral también te ayudará a elegir la mejor forma de expresarte según la situación, asegurando que tu mensaje sea claro y apropiado. Agradezco tu esfuerzo en realizar la actividad y en seguir las normas de netiqueta en los entornos virtuales de aprendizaje.

En el primer ejercicio, tu relato sobre la historia de tu vida ha sido interesante y demuestra un buen desarrollo de ideas. Sin embargo, es importante que profundices más en ciertos aspectos para dar mayor riqueza a tu narrativa. Asegúrate también de seguir las características solicitadas en las instrucciones del formato y la extensión. Para desarrollar más tus ideas, podrías incluir anécdotas que ofrezcan más contexto y color a tu relato.

En el ejercicio 2, has intentado identificar algunas categorías gramaticales, pero he identificado vrios errores. Sería beneficioso dedicar tiempo adicional a repasar estos conceptos para reforzar tu comprensión. Este repaso te ayudará a sentirte más seguro al aplicar las categorías gramaticales en tus trabajos escolares. Por ejemplo, al comprender mejor cómo se usan los verbos, sustantivos, adjetivos, adverbios, artículos y preposiciones, podrás mejorar la claridad y cohesión de tus escritos, facilitando así tu éxito académico y comunicativo.

Puedo ver que se te ha complicado realizar y compartir tu grabación. Espero este recurso te pueda ser útil para compartir tus audios y videos en futuras actividades: https://youtu.be/uZboUIr54Gw.

En el ejercicio final, puedo notar que se te ha complicado realizar el párrafo sobre las diferencias encontradas al expresarte de manera oral y escrita. Es importante realizar estos ejercicios, pues te permiten reflexionar sobre tus fortalezas y áreas de oportunidad. 

Por otro lado, puedo ver que has empleado la tecnología para generar tu documento con la información solicitada; sin embargo, dejaste de lado muchas de las instrucciones para la elaboración de la actividad. Te sugiero que revises detalladamente las instrucciones para las próximas actividades, de manera que puedas obtener un mejor puntaje. Si tienes dudas durante el proceso, no dudes en escribirme por el chat para resolverlas y participar en los espacios abiertos, lo cual te ayudará a realizar una buena actividad. Enviaste correctamente el archivo en el espacio destinado y lo has nombrado como se solicita en las instrucciones. Has entregado en el tiempo establecido tu documento, sin algún retraso.

En cuanto al criterio comunicativo, hace falta trabajar un poco en la manera en que organizas la información para que puedas presentarla de manera clara, coherente y precisa. Cuida mucho el formato del texto para que sea homogéneo y asegúrate de que tus respuestas estén siempre apegadas a lo que se te solicita. Presentas algunas faltas de ortografía y sintaxis, por lo que antes de enviar tus actividades te recomiendo que utilices un revisor de ortografía como LanguageTool. Te dejo un tutorial para que veas cómo utilizarlo: https://youtu.be/Zg4Ua3G8wkU.

Para el criterio de pensamiento crítico, te recomendaría comenzar revisando los recursos proporcionados en el curso y las grabaciones de las sesiones de espacio abierto en vivo, para asegurarte de estar al día con el contenido. Es importante que retomes esta tarea para desarrollar tu habilidad de distinguir entre estos dos tipos de expresión y comprender cómo se estructura el lenguaje. 

Después de haber visto este tema me parece que este recurso podría complementar lo que vimos. Te puede ayudar a profundizar en las categorías gramaticales, y cómo las puedes manejar de la mejora manera. Te recomiendo revisarlo: 
https://e1.portalacademico.cch.unam.mx/alumno/tlriid2/unidad1/catGramaticales/clasesDePalabras1

Finalmente, analizando la retroalimentación que te he dado, ¿qué pasos podrías seguir para autoevaluar tu progreso en estas temáticas que vimos? Ánimo, sé que alcanzar la meta en algunas ocasiones es cansado y desgastante, pero valdrá la pena. Sigue las sugerencias, analiza las instrucciones, entra los espacios abiertos y revisa las rúbricas de evaluación, verás que podrás obtener mejores puntajes. Las calificaciones no definen tu valía como estudiante, lo importante es tu compromiso y perseverancia al completar las actividades. Aprende de los desafíos y utiliza la retroalimentación para crecer y mejorar. Me despido reiterando mi reconocimiento por tu esfuerzo y poniéndome a tu disposición por si tuvieras alguna duda respecto a tu calificación o retroalimentación.
Saludos,

Ricardo Raúl Estrada Pérez
Asesor Virtual
M2C1G82-021.
```

Calificación:44
```
Hola Fátima:

Espero que esta actividad te haya sido útil para recordar las clases de palabras y diferenciar entre la comunicación escrita y la oral. Identificar verbos, sustantivos, adjetivos, adverbios, artículos y preposiciones es esencial en la vida cotidiana, ya que te ayuda a comprender y utilizar el lenguaje con mayor eficacia. Aunque hubo algunos desafíos, con un poco más de dedicación y estudio, estoy seguro de que puedes mejorar significativamente tu comprensión de estos temas. Diferenciar entre la comunicación escrita y oral también es importante, ya que te permitirá comunicarte de manera más adecuada en diversas situaciones. Agradezco tu esfuerzo en realizar la actividad y en seguir las normas de netiqueta en los entornos virtuales de aprendizaje.

En el primer ejercicio, tu relato sobre la historia de tu vida ha sido interesante y muestra un buen desarrollo de ideas. Sería recomendable que profundices más en algunos puntos clave para darle más profundidad a tu narrativa. Además, es esencial que te apegues a las instrucciones del formato y la extensión solicitada. Para desarrollar más tus ideas, podrías usar citas o referencias que respalden tus puntos y hagan tu relato más convincente.

No completaste el ejercicio 2, donde era necesario identificar los verbos, sustantivos, adjetivos, adverbios, artículos y preposiciones. Es crucial realizar este ejercicio incluso después de entregar la actividad, ya que te ayudará a reforzar tus habilidades gramaticales. Dominar estas categorías gramaticales es fundamental para mejorar tu comprensión de textos y tu habilidad para comunicarte efectivamente en futuras tareas y actividades académicas. 

Puedo ver que se te ha complicado realizar y compartir tu grabación. Espero este recurso te pueda ser útil para compartir tus audios y videos en futuras actividades: https://youtu.be/uZboUIr54Gw.

En el ejercicio final, puedo notar que se te ha complicado realizar el párrafo sobre las diferencias encontradas al expresarte de manera oral y escrita. Es importante realizar estos ejercicios, pues te permiten reflexionar sobre tus fortalezas y áreas de oportunidad. 

Por otro lado, puedo ver que has empleado la tecnología para generar tu documento con la información solicitada; sin embargo, dejaste de lado muchas de las instrucciones para la elaboración de la actividad. Te sugiero que revises detalladamente las instrucciones para las próximas actividades, de manera que puedas obtener un mejor puntaje. Si tienes dudas durante el proceso, no dudes en escribirme por el chat para resolverlas y participar en los espacios abiertos, lo cual te ayudará a realizar una buena actividad. Enviaste correctamente el archivo en el espacio destinado y lo has nombrado como se solicita en las instrucciones. Has entregado en el tiempo establecido tu documento, sin algún retraso.

En cuanto al criterio comunicativo, organizas toda la información de manera clara, coherente y precisa. No presentas errores en sintaxis, ortografía o puntuación, y presentas las ideas de manera lógica y congruente. Recuerda que siempre puedes utilizar revisores de ortografía como LenguageTool para revisar tus escritos. Te dejo un tutorial para que veas cómo utilizarlo: https://youtu.be/Zg4Ua3G8wkU.

Para el criterio de pensamiento crítico, te recomendaría comenzar revisando los recursos proporcionados en el curso y las grabaciones de las sesiones de espacio abierto en vivo, para asegurarte de estar al día con el contenido. Es importante que retomes esta tarea para desarrollar tu habilidad de distinguir entre estos dos tipos de expresión y comprender cómo se estructura el lenguaje. 

Después de haber visto este tema me parece que este recurso podría complementar lo que vimos, resume en parte las clases de palabras y te ofrecen algunos ejercicios para seguir practicando su clasificación, te recomiendo revisarlo http://cea.cide.edu/gramtica/tipos_de_palabras.html.

Para concluir, tras revisar la identificación de clases de palabras (verbos, sustantivos, adjetivos, etc.) ¿por qué es importante dominar la clasificación de las clases de palabras como estudiantes de Prepa en Línea? Ánimo, sé que alcanzar la meta en algunas ocasiones es cansado y desgastante, pero valdrá la pena. Sigue las sugerencias, analiza las instrucciones, entra los espacios abiertos y revisa las rúbricas de evaluación, verás que podrás obtener mejores puntajes. Las calificaciones no definen tu valía como estudiante, lo importante es tu compromiso y perseverancia al completar las actividades. Aprende de los desafíos y utiliza la retroalimentación para crecer y mejorar. Me despido reiterando mi reconocimiento por tu esfuerzo y poniéndome a tu disposición por si tuvieras alguna duda respecto a tu calificación o retroalimentación.
Saludos,

Ricardo Raúl Estrada Pérez
Asesor Virtual
M2C1G82-021.
```

Calificación:90
```
Hola Kevin:

Tu desempeño ha sido satisfactorio, y espero que esta actividad te haya ayudado a recordar las clases de palabras y a diferenciar entre la comunicación escrita y la oral. Poder identificar verbos, sustantivos, adjetivos, adverbios, artículos y preposiciones es una habilidad muy valiosa en la vida cotidiana, ya que facilita una comunicación más clara y precisa. Además, comprender las diferencias entre la comunicación escrita y oral te permitirá adaptar tu mensaje a diferentes contextos, mejorando así tu efectividad comunicativa. Con un poco más de dedicación, estoy seguro de que podrás profundizar en estos temas y alcanzar un nivel superior. Quiero destacar tu esfuerzo en realizar la actividad y en seguir las normas de netiqueta en los entornos virtuales de aprendizaje.

En el primer ejercicio, tu relato sobre la historia de tu vida ha sido interesante y lo has realizado apegándote al formato solicitado, así como a la extensión requerida. Al momento de realizar relatos, te sugiero prestar atención a la estructura narrativa, asegurando un inicio, desarrollo y cierre claros. Esto mejorará aún más la claridad y el impacto de tus historias.

En el ejercicio 2, has puesto empeño en identificar diferentes categorías gramaticales como verbos, sustantivos, adjetivos, adverbios, artículos y preposiciones. Sería beneficioso repasar estos elementos, considerando que algunas palabras no fueron clasificadas como se esperaba inicialmente. Entender cómo funcionan las palabras en una frase te permitirá escribir con coherencia y estructura, lo cual es esencial tanto en estudios académicos como en la comunicación diaria.

Has grabado un relato de tu vida que cumple con la duración requerida y lo has compartido correctamente en el ejercicio 3. Sé que el proceso de grabar puede ser complicado y que a menudo se necesitan varios intentos, y tu dedicación para completar este ejercicio es destacable.

Tu párrafo en el ejercicio final aborda las diferencias entre la expresión oral y escrita, aunque no llega a la longitud requerida. Para mejorar, te recomiendo detallar más tus ideas y apoyar tus puntos con ejemplos específicos. Considera hacer una lista de los aspectos que quieres cubrir antes de empezar a escribir para asegurarte de que no omites nada importante.

Por otro lado, puedo ver que has empleado la tecnología para generar tu documento con toda la información solicitada, siguiendo todas las instrucciones para la elaboración de la actividad. Enviaste correctamente el archivo en el espacio destinado y lo has nombrado como se solicita en las instrucciones. Has entregado en el tiempo establecido tu documento, sin algún retraso.

En cuanto al criterio comunicativo, organizas toda la información de manera clara, coherente y precisa. Presentas algunas faltas de ortografía y sintaxis, por lo que antes de enviar tus actividades te recomiendo que utilices un revisor de ortografía como LanguageTool. Te dejo un tutorial para que veas cómo utilizarlo: https://youtu.be/Zg4Ua3G8wkU.

Has abordado las diferencias entre la comunicación oral y escrita de manera general, pero podrías beneficiarte de un análisis más profundo. También sería útil repasar las clases de palabras, como verbos, sustantivos, adjetivos, adverbios, artículos y preposiciones. Te recomiendo utilizar las herramientas en línea y aplicaciones educativas que les he compartido en el foro aprendiendo y en los recursos complementario, considero que te ayudarán a reforzar estos conceptos. 

Después de haber visto este tema me parece que este recurso podría complementar lo que vimos. Te puede ayudar a profundizar en las categorías gramaticales, y cómo las puedes manejar de la mejora manera. Te recomiendo revisarlo: 
https://e1.portalacademico.cch.unam.mx/alumno/tlriid2/unidad1/catGramaticales/clasesDePalabras1

Ya para cerrar, sabemos que la clasificación de las palabras es algo que nos requirió esfuerzo y dedicación, ¿qué estrategias podrías implementar para mejorar tu habilidad en la identificación precisa de verbos, sustantivos y otros elementos del discurso? Lo has hecho bien, reconozco tu esfuerzo y dedicación. El aprendizaje es continuo, cada paso cuenta en tu desarrollo académico, sigue adelante con determinación, tu dedicación es clave para alcanzar metas. Me despido reiterando mi reconocimiento por tu esfuerzo y poniéndome a tu disposición por si tuvieras alguna duda respecto a tu calificación o retroalimentación.
Saludos,

Ricardo Raúl Estrada Pérez
Asesor Virtual
M2C1G82-021.
```

Calificación:
```
```
---

## 7. Uso con Ollama (ejemplo de invocación)

```bash
# Con system prompt en archivo
ollama run mistral -f system_prompt.txt

# O enviando el JSON de evaluación como contexto
# El prompt del usuario sería algo como:
# "Genera la retroalimentación para esta evaluación: [JSON]"
```

**User prompt sugerido:**
```
Usando los datos de evaluación que te proporciono, genera una retroalimentación siguiendo la estructura y el mapeo de frases del documento de referencia. Escribe solo la retroalimentación, sin explicaciones adicionales.

Datos de evaluación:
[JSON aquí]
```
