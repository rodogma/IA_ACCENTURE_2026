
import json
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent
ARCHIVO = BASE / "registros_latencia_costo.jsonl"

# Configura aqui las tarifas oficiales de tu modelo,
# expresadas en USD por 1 millon de tokens.
PRECIO_ENTRADA = os.getenv("PRECIO_ENTRADA_MILLON_USD")
PRECIO_SALIDA = os.getenv("PRECIO_SALIDA_MILLON_USD")

if not ARCHIVO.exists():
    raise FileNotFoundError(
        "Primero ejecuta registro_rag.py para generar el JSONL."
    )

if not PRECIO_ENTRADA or not PRECIO_SALIDA:
    raise ValueError(
        "Faltan las tarifas. Configura las variables "
        "PRECIO_ENTRADA_MILLON_USD y "
        "PRECIO_SALIDA_MILLON_USD."
    )

precio_entrada = float(PRECIO_ENTRADA)
precio_salida = float(PRECIO_SALIDA)

registros = []

with ARCHIVO.open("r", encoding="utf-8") as archivo:
    for linea in archivo:
        if linea.strip():
            registros.append(json.loads(linea))

costo_total = 0.0

for registro in registros:
    tokens = registro.get("tokens", {})

    entrada = tokens.get("input_tokens", 0)
    salida = tokens.get("output_tokens", 0)

    costo = (
        entrada * precio_entrada / 1_000_000
        + salida * precio_salida / 1_000_000
    )

    registro["costo_generacion_usd"] = round(costo, 10)
    costo_total += costo

# Guardar una copia de seguridad antes de modificar el archivo.
RESPALDO = BASE / "registros_latencia_costo_respaldo.jsonl"
RESPALDO.write_bytes(ARCHIVO.read_bytes())

with ARCHIVO.open("w", encoding="utf-8") as archivo:
    for registro in registros:
        archivo.write(
            json.dumps(registro, ensure_ascii=False) + "\n"
        )

print("================================")
print(" COSTOS RAG CALCULADOS")
print("================================")
print(f"Registros actualizados: {len(registros)}")
print(f"Costo total estimado: ${costo_total:.8f} USD")
print(f"Archivo actualizado: {ARCHIVO}")
print(f"Copia de seguridad: {RESPALDO}")
