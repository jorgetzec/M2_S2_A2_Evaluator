import os
import json
import sys
import tempfile
from pdf2docx import Converter

# Asegurar que el directorio del script está en el path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from processor_v4 import process_docx_v4

def batch_process():
    entradas_dir = "/home/node/entradas"
    reportes_dir = "/home/node/reportes/jsons"
    
    # Crear carpeta de reportes si no existe
    if not os.path.exists(reportes_dir):
        os.makedirs(reportes_dir)
        print(f"Directorio creado: {reportes_dir}")

    files = [f for f in os.listdir(entradas_dir) if os.path.isfile(os.path.join(entradas_dir, f))]
    
    # Extensiones soportadas
    valid_extensions = ('.docx', '.pdf')
    
    processed_count = 0
    errors_count = 0

    for filename in files:
        if not filename.lower().endswith(valid_extensions):
            continue
            
        file_path = os.path.join(entradas_dir, filename)
        json_filename = os.path.splitext(filename)[0] + ".json"
        output_path = os.path.join(reportes_dir, json_filename)
        
        print(f"Procesando: {filename}...", end=" ", flush=True)
        
        temp_docx = None
        try:
            # Lógica de PDF a DOCX (copiada de processor_v4.py)
            if filename.lower().endswith(".pdf"):
                temp_dir = tempfile.gettempdir()
                filename_base = filename.rsplit(".", 1)[0]
                temp_docx = os.path.join(temp_dir, f"{filename_base}_temp_batch.docx")
                
                cv = Converter(file_path)
                cv.convert(temp_docx, start=0, end=None)
                cv.close()
                processing_path = temp_docx
            else:
                processing_path = file_path

            # Procesar el archivo
            result = process_docx_v4(processing_path)
            
            # Restaurar nombre original si era PDF
            if filename.lower().endswith(".pdf"):
                result["filename"] = filename

            # Guardar JSON
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print("OK")
            processed_count += 1
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            errors_count += 1
        finally:
            if temp_docx and os.path.exists(temp_docx):
                try:
                    os.remove(temp_docx)
                except:
                    pass

    print("-" * 30)
    print(f"Procesamiento terminado.")
    print(f"Archivos procesados correctamente: {processed_count}")
    print(f"Errores encontrados: {errors_count}")
    print(f"Los resultados están en: {reportes_dir}")

if __name__ == "__main__":
    batch_process()
