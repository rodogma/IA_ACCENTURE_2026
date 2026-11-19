
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("No se encontro la API Key en .env")

cliente = genai.Client(api_key=api_key)

print("Buscando modelos Gemini disponibles...")

try:
    modelos = list(cliente.models.list())
except Exception as error:
    print("Error al consultar modelos:", error)
    raise

candidatos = []

for modelo in modelos:
    acciones = getattr(modelo, "supported_actions", []) or []
    nombre = modelo.name.replace("models/", "")

    if "generateContent" in acciones and "gemini" in nombre.lower():
        candidatos.append(nombre)

# Preferir modelos Flash, normalmente mas rapidos.
candidatos.sort(
    key=lambda nombre: (
        "flash" not in nombre.lower(),
        "lite" not in nombre.lower(),
        nombre
    )
)

if not candidatos:
    print("No se encontraron modelos de generacion disponibles.")
    raise SystemExit(1)

print("\nModelos encontrados:")
for nombre in candidatos:
    print("-", nombre)

modelo_funcional = None

for nombre in candidatos:
    print(f"\nProbando: {nombre}")

    try:
        respuesta = cliente.models.generate_content(
            model=nombre,
            contents="Responde solamente OK",
        )

        texto = respuesta.text or ""

        if texto.strip():
            print("RESPUESTA:", texto)
            modelo_funcional = nombre
            break

    except Exception as error:
        print("No funciono:", str(error)[:250])

if modelo_funcional:
    print("\n================================")
    print("MODELO QUE RESPONDIO:")
    print(modelo_funcional)
    print("================================")
else:
    print("\nNingun modelo respondio correctamente.")
    print("Puede existir un problema temporal de API, cuota o conexion.")
