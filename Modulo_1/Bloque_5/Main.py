from  Aritmetica import sumar
import json

print ("prueba de modulo d artmetica")

print (sumar(5,3))

# crear json

respuesta_json = '{"texto": "Hola, soy una respuesta generada", "detalles": {"modelo": "nombre-del-modelo", "tokens": 12}}'
respuesta = json.loads(respuesta_json)

print (type(respuesta_json))
respuesta_dics = json.loads(respuesta_json)
print (type(respuesta_dics))
print (respuesta_dics)
print(respuesta_dics["texto"])
print(respuesta_dics["detalles"]["modelo"])