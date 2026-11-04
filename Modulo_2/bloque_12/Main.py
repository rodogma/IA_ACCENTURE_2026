from Consumir_gemini import obtener_dato_de_prueba

respuesta1 = obtener_dato_de_prueba(
    "¿Cuál es la capital de Inglaterra?",
    "Responde de forma breve y en español."
)

print("Respuesta 1:", respuesta1)

respuesta2 = obtener_dato_de_prueba(
    "¿Cuánto es 1 + 2?",
    "Responde solamente con el resultado."
)

print("Respuesta 2:", respuesta2)