
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma


# ==========================================
# BLOQUE 26 - RECUPERACIÓN SEMÁNTICA
# ==========================================

# 1. LOCALIZAR LA RAÍZ DEL PROYECTO

RUTA_PROYECTO = Path(__file__).resolve().parents[2]

RUTA_ENV = RUTA_PROYECTO / ".env"

load_dotenv(dotenv_path=RUTA_ENV)

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError(
        "No se encontró GEMINI_API_KEY ni GOOGLE_API_KEY "
        f"en el archivo {RUTA_ENV}"
    )


# ==========================================
# 2. CONFIGURAR EMBEDDINGS
# ==========================================

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=API_KEY,
)


# ==========================================
# 3. CARGAR CHROMA
# ==========================================

# Usamos el índice creado en el Bloque 24.
RUTA_VECTORSTORE = (
    RUTA_PROYECTO
    / "Modulo_2"
    / "bloque_24"
    / "vectorstore"
)

NOMBRE_COLECCION = "corpus_bloque_24"

if not RUTA_VECTORSTORE.exists():
    raise FileNotFoundError(
        f"No existe la carpeta: {RUTA_VECTORSTORE}\n"
        "Ejecuta primero el indexador del Bloque 24."
    )

vectorstore = Chroma(
    collection_name=NOMBRE_COLECCION,
    persist_directory=str(RUTA_VECTORSTORE),
    embedding_function=embeddings,
    create_collection_if_not_exists=False,
)

cantidad = vectorstore._collection.count()

print("\n========================================")
print("BLOQUE 26 - RECUPERACIÓN SEMÁNTICA")
print("========================================")

print("\nRuta:", RUTA_VECTORSTORE)
print("Colección:", NOMBRE_COLECCION)
print("Chunks almacenados:", cantidad)

if cantidad == 0:
    raise ValueError(
        "La colección está vacía. "
        "Primero debes indexar los documentos."
    )


# ==========================================
# 4. FUNCIÓN DE REINTENTOS
# ==========================================

def con_reintentos(operacion, max_intentos=4):
    espera = 5

    for intento in range(1, max_intentos + 1):
        try:
            return operacion()

        except Exception as error:
            mensaje = str(error).lower()

            es_temporal = any(
                codigo in mensaje
                for codigo in [
                    "429",
                    "resource_exhausted",
                    "503",
                    "unavailable",
                    "timeout",
                ]
            )

            if not es_temporal or intento == max_intentos:
                raise

            print(
                f"\nError temporal de Gemini. "
                f"Reintentando en {espera} segundos..."
            )

            time.sleep(espera)
            espera *= 2


# ==========================================
# 5. SIMILARITY SEARCH
# ==========================================

print("\n========================================")
print("PRUEBA 1 - SIMILARITY SEARCH")
print("========================================")

pregunta_1 = (
    "¿Qué maquinaria necesito para nivelar un terreno?"
)

resultados = con_reintentos(
    lambda: vectorstore.similarity_search(
        pregunta_1,
        k=1,
    )
)

print("\nPregunta:", pregunta_1)

for resultado in resultados:
    print("\nContenido:")
    print(resultado.page_content)


# ==========================================
# 6. SIMILARITY SEARCH WITH SCORE
# ==========================================

print("\n========================================")
print("PRUEBA 2 - SIMILARITY SEARCH WITH SCORE")
print("========================================")

pregunta_2 = (
    "¿Qué equipo puedo utilizar "
    "para construir cimientos?"
)

resultados_con_score = con_reintentos(
    lambda: vectorstore.similarity_search_with_score(
        pregunta_2,
        k=5,
    )
)

print("\nPregunta:", pregunta_2)

for documento, score in resultados_con_score:
    print("\nScore:", round(score, 4))
    print("Contenido:", documento.page_content[:150])


# ==========================================
# 7. RETRIEVER
# ==========================================

print("\n========================================")
print("PRUEBA 3 - RETRIEVER")
print("========================================")

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3}
)

pregunta_3 = (
    "¿Cuándo necesita un agente "
    "aprobación humana?"
)

resultados = con_reintentos(
    lambda: retriever.invoke(pregunta_3)
)

print("\nPregunta:", pregunta_3)

for resultado in resultados:
    print("\nContenido:", resultado.page_content)
    print("Metadata:", resultado.metadata)


print("\n========================================")
print("BLOQUE 26 FINALIZADO CORRECTAMENTE")
print("========================================")
