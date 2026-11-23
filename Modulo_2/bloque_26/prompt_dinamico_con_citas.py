
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma


# ==================================================
# BLOQUE 26 - PROMPT DINAMICO CON FUENTES CITADAS
# ==================================================

# 1. CONFIGURACION

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]

load_dotenv(RAIZ_PROYECTO / ".env")

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError(
        "No se encontro GEMINI_API_KEY en el archivo .env"
    )

RUTA_VECTORSTORE = (
    RAIZ_PROYECTO / "Modulo_2" / "bloque_24" / "vectorstore"
)

NOMBRE_COLECCION = "corpus_bloque_24"

MODELO_CHAT = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


# ==================================================
# 2. PLANTILLA DEL PROMPT
# ==================================================

PROMPT_TEMPLATE = """
Responde la pregunta usando SOLO el contexto de abajo.

Cita la fuente de cada afirmacion utilizando su numero
entre corchetes, por ejemplo: [1] o [2].

Si el contexto no contiene informacion suficiente,
debes decirlo claramente. No inventes datos.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:
"""


# ==================================================
# 3. REINTENTOS PARA ERRORES TEMPORALES
# ==================================================

def con_reintentos(operacion, max_intentos=4):
    espera = 5

    for intento in range(1, max_intentos + 1):
        try:
            return operacion()

        except Exception as error:
            mensaje = str(error).lower()

            temporal = any(
                codigo in mensaje
                for codigo in [
                    "429",
                    "resource_exhausted",
                    "503",
                    "unavailable",
                    "timeout",
                ]
            )

            if not temporal or intento == max_intentos:
                raise

            print(
                f"\nError temporal de Gemini. "
                f"Reintentando en {espera} segundos..."
            )

            time.sleep(espera)
            espera *= 2


# ==================================================
# 4. FORMATEAR CONTEXTO Y CITAS
# ==================================================

def formatear_contexto(chunks_recuperados):
    """
    Construye un contexto numerado y un diccionario
    que relaciona cada numero con su fuente.
    """

    lineas = []
    citas = {}

    for numero, documento in enumerate(
        chunks_recuperados,
        start=1,
    ):
        fuente = documento.metadata.get(
            "fuente",
            "desconocida",
        )

        lineas.append(
            f"[{numero}] {documento.page_content}"
        )

        citas[numero] = fuente

    contexto = "\n\n".join(lineas)

    return contexto, citas


# ==================================================
# 5. CARGAR VECTOR STORE EXISTENTE
# ==================================================

def cargar_vectorstore():

    if not RUTA_VECTORSTORE.exists():
        raise FileNotFoundError(
            f"No existe el indice:\n{RUTA_VECTORSTORE}\n"
            "Ejecuta primero el Bloque 24."
        )

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=API_KEY,
    )

    vectorstore = Chroma(
        collection_name=NOMBRE_COLECCION,
        persist_directory=str(RUTA_VECTORSTORE),
        embedding_function=embeddings,
        create_collection_if_not_exists=False,
    )

    cantidad = vectorstore._collection.count()

    print("\nRuta del indice:", RUTA_VECTORSTORE)
    print("Coleccion:", NOMBRE_COLECCION)
    print("Chunks almacenados:", cantidad)

    if cantidad == 0:
        raise ValueError(
            "La coleccion esta vacia. "
            "Debes indexar los documentos del Bloque 24."
        )

    return vectorstore


# ==================================================
# 6. CONSTRUIR PROMPT DINAMICO
# ==================================================

def construir_prompt(pregunta, vectorstore, k=3):

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": k}
    )

    chunks_recuperados = con_reintentos(
        lambda: retriever.invoke(pregunta)
    )

    contexto, citas = formatear_contexto(
        chunks_recuperados
    )

    prompt = PROMPT_TEMPLATE.format(
        contexto=contexto,
        pregunta=pregunta,
    )

    return prompt, citas


# ==================================================
# 7. CONSULTAR MODELO GEMINI
# ==================================================

def generar_respuesta(prompt):

    modelo = ChatGoogleGenerativeAI(
        model=MODELO_CHAT,
        google_api_key=API_KEY,
        temperature=0,
        max_retries=2,
    )

    respuesta = con_reintentos(
        lambda: modelo.invoke(prompt)
    )

    contenido = respuesta.content

    if isinstance(contenido, str):
        return contenido

    if isinstance(contenido, list):
        return "\n".join(
            bloque.get("text", "")
            for bloque in contenido
            if isinstance(bloque, dict)
            and bloque.get("type") == "text"
        )

    return str(contenido)


# ==================================================
# 8. PROBAR DOS PREGUNTAS
# ==================================================

def main():

    print("\n========================================")
    print("BLOQUE 26 - PROMPT DINAMICO CON CITAS")
    print("========================================")

    vectorstore = cargar_vectorstore()

    preguntas = [
        "¿Que maquinaria se recomienda para nivelar un terreno?",
        "¿Cuando necesita un agente aprobacion humana?",
        "¿Cual es la temperatura de Marte hoy?",
    ]

    for numero, pregunta in enumerate(
        preguntas,
        start=1,
    ):

        print("\n" + "=" * 60)
        print(f"PRUEBA {numero}")
        print("=" * 60)

        prompt, citas = construir_prompt(
            pregunta=pregunta,
            vectorstore=vectorstore,
            k=3,
        )

        print("\nPREGUNTA:")
        print(pregunta)

        print("\nPROMPT DINAMICO:")
        print(prompt)

        print("\nDICCIONARIO DE CITAS:")
        print(citas)

        if "desconocida" in citas.values():
            print(
                "\nADVERTENCIA: Faltan metadatos 'fuente' "
                "en algunos documentos."
            )

        print("\nRESPUESTA DE GEMINI:")

        respuesta = generar_respuesta(prompt)

        print(respuesta)

    print("\n========================================")
    print("BLOQUE 26 FINALIZADO")
    print("========================================")


if __name__ == "__main__":
    main()
