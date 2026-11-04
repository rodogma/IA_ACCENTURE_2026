
import os
from dotenv import load_dotenv
from cliente import consultar_modelo

load_dotenv()

print("\nPRUEBA: CREDENCIAL INVÁLIDA REAL")

# Guardar la clave verdadera
clave_original = os.getenv("GEMINI_API_KEY")

try:
    # Reemplazar temporalmente por clave falsa
    os.environ["GEMINI_API_KEY"] = "AIza123456789CLAVEFALSA"

    # Consulta real a Gemini
    respuesta = consultar_modelo("Hola")

    print("FALLIDA: Se esperaba un error")
    print(respuesta)

except ValueError as error:
    print("Error de autenticación:", error)
    print("PRUEBA: CORRECTA")

except Exception as error:
    print("Error recibido:", type(error).__name__, error)
    print("Revisar clasificación del error")

finally:
    # Restaurar la clave verdadera
    if clave_original is None:
        os.environ.pop("GEMINI_API_KEY", None)
    else:
        os.environ["GEMINI_API_KEY"] = clave_original

    print("Clave original restaurada")
