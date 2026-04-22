"""
Helper v4 – Llama a la API de Ollama desde un nodo Execute Command de n8n.

Uso: echo '<JSON base64>' | base64 -d | python3 ollama_call_v4.py
  o: python3 ollama_call_v4.py <archivo_prompt.json>

Entrada (JSON): {"system": "...", "user": "...", "model": "mistral"}
Salida: JSON de la respuesta de Ollama en stdout.

Esto evita problemas de codificación del HTTP Request de n8n con el modo
Raw/JSON cuando el texto contiene caracteres especiales.
"""

import sys
import json
import urllib.request


OLLAMA_URL = "http://host.docker.internal:11434/api/chat"
TIMEOUT = 180  # segundos


def call_ollama(system_prompt, user_prompt, model="mistral"):
    """Llama a Ollama /api/chat y devuelve el dict de respuesta."""
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req, timeout=TIMEOUT)
    return json.loads(resp.read().decode("utf-8"))


def main():
    # Leer input: desde archivo (arg) o desde stdin
    if len(sys.argv) > 1 and sys.argv[1] != "-":
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            input_data = json.load(f)
    else:
        input_data = json.loads(sys.stdin.read())

    system_prompt = input_data.get("system", "")
    user_prompt = input_data.get("user", "")
    model = input_data.get("model", "mistral")

    try:
        result = call_ollama(system_prompt, user_prompt, model)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e), "message": {"content": ""}}))


if __name__ == "__main__":
    main()
