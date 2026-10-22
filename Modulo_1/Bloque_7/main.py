
from consumir_api_3 import obtener_dato_de_prueba

try:
    pregunta = "¿Cuál es la capital de Inglaterra?"

    resultado = obtener_dato_de_prueba(pregunta)

    print("Respuesta de Gemini:")
    print(resultado)

except (TypeError, ValueError) as error:
    print("Error de validación:", error)

except Exception as error:
    print("Error al consultar Gemini:", error)
