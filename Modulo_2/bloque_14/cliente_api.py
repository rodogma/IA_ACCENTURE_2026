# cliente_api.py

def armar_peticion(pregunta, system_instruction=""):
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía")

    cuerpo = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": pregunta.strip()}]
            }
        ]
    }

    if system_instruction:
        cuerpo["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    return cuerpo


def extraer_texto(respuesta):
    candidatos = respuesta.get("candidates", [])

    if not candidatos:
        raise ValueError("Gemini no devolvió candidatos")

    partes = candidatos[0].get(
        "content", {}
    ).get("parts", [])

    textos = [
        parte["text"]
        for parte in partes
        if isinstance(parte.get("text"), str)
    ]

    if not textos:
        raise ValueError("Gemini no devolvió texto")

    return "\n".join(textos)