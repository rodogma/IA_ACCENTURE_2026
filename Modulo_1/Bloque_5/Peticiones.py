
import json
import requests


# Crear el cuerpo JSON
def create_payload(prompt):
    return json.dumps({
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    })


# Crear encabezados HTTP
def create_headers(api_key):
    return {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }


# Realizar petición a Gemini

import time
import requests

def make_request(url, api_key, prompt):
    if not api_key:
        return {"error": "No se encontró la API Key"}

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    for intento in range(3):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code in (429, 503):
                if intento < 2:
                    espera = 2 ** intento
                    print(f"Servicio ocupado. Reintentando en {espera}s...")
                    time.sleep(espera)
                    continue

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    return {"error": "No fue posible completar la solicitud"}
