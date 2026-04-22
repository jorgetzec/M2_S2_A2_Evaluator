Tenemos este flujo en n8n montado en un docker, pero no me está resultando práctico. En ocasiones, los estudiantes mandan mal su trabajo o en otro orden o con otro formato y ya no se puede analizar. QUiero crear una nueva versión, pero ahora no un n8n, una aplicación de steamlit, usando docker, que me permita lo siguiente:
- Un panel donde suba el archivo, reconozca si es word. Procesar html.
- Si es pdf, powerpoint, etc, pueda convertirlo a html.
-Poner el documento en un panel para que le diga qué sección es cada cosa. Donde está el ejercicio 1, 2,3,..
- Poder corregir el enlace si no está correcto. 
- QUe corra algo similar a lo que hace ahora el processor_v4.py
 pero en procesos modulares para al finar obtener un json condensaso sin que sea repetitivo, lo mas compacto, o en TOON (Token-Oriented Object Notation), para que sea mas compacto. Las principales features:
-- Contabilice la extensión del relato.
--Identifique las palabras resaltadas. Contabilice y ponga cuales están correctas y cuales no.
--Extraiga la transcripción del audio si está presente
--Analice la relfexión final.
-- Extraiga fragmentos de cada segmento para poder generar una retroalimentación personalizada.
--Evalué ortografía
--Comprueba si el relato y la transcripción son identicos o tienen fragmentos identicos que indique evitar lectura.
--Que aplique la rúbrica para tener la calificación y el nivel alcanzado para cada criterio /doc/03_data_AI2/m2_ai2_rubrica.md
--Que pueda descargar el archivo json o TOON.
--Que tenga una interfase que me permita ver la información rápidamente.
--Idealmente que genera una retroalimentación usando algun modelo de LLM sin que sea costoso, ya sea gemini o kimi o esas que tengan suficientes tokes y no necesite pagar. 
--Que la retroalimentacion sigue una plantilla, pero que sea personalizada, empática... etc. que sugiera manteriales para mejorar segun un listado para la actvividad integradora 2 (M=2, AI2) /docs/01_guidas/Compilado M02_RED_DSAyDC.csv
- Todo esto debe generarse en D:\CODE\Code3_Coding and Data\20260318_M02S1AI2_app_evaluador.
El panel debe considerar si entrega otro formato como audio mp3 o videos mp4 o incluso imagenes. NO sé si es posible evaluar eso? extractor de texto en imagenes? videos a frames para extraer texto y voz por separado? Que la interfase incluya la opción, si el estudiante entrega otra cosa o no se procesa bien, tener un formulario para evaluarlo manualmente segun la rúbrica. 