from dotenv import load_dotenv #importando  funcion load_dotenv
import os     # importando el modelo os para acceder avariables de entorno


load_dotenv()   # cargar las variables de entorno
print(os.getenv("GEMINI_API_KEY")) #impimiendo todas las variables de entorno cargadas 