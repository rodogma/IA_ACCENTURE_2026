
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command


# ==================================================
# ESTADO DEL DESPLIEGUE
# ==================================================

class EstadoDespliegue(TypedDict):
    huella_nueva: str
    aprobado: bool


# ==================================================
# NODO 1: PROPONER VERSION
# ==================================================

def proponer(estado: EstadoDespliegue):

    print(
        "Proponiendo nueva version:",
        estado["huella_nueva"]
    )

    return {}


# ==================================================
# NODO 2: SUPERVISION HUMANA
# ==================================================

def supervisar(estado: EstadoDespliegue):

    decision = interrupt({
        "motivo": "Aprobar nueva version de prompt en produccion",
        "huella_propuesta": estado["huella_nueva"]
    })

    if not isinstance(decision, bool):
        raise ValueError(
            "La decision debe ser True o False"
        )

    return {"aprobado": decision}


# ==================================================
# NODO 3: APLICAR O RECHAZAR
# ==================================================

def aplicar(estado: EstadoDespliegue):

    if estado["aprobado"]:

        print(
            "VERSION",
            estado["huella_nueva"],
            "ACTIVADA"
        )

    else:

        print(
            "VERSION",
            estado["huella_nueva"],
            "RECHAZADA. Se mantiene la anterior."
        )

    return {}


# ==================================================
# CONSTRUIR GRAFO
# ==================================================

grafo = StateGraph(EstadoDespliegue)

grafo.add_node("proponer", proponer)
grafo.add_node("supervisar", supervisar)
grafo.add_node("aplicar", aplicar)

grafo.add_edge(START, "proponer")
grafo.add_edge("proponer", "supervisar")
grafo.add_edge("supervisar", "aplicar")
grafo.add_edge("aplicar", END)

app_despliegue = grafo.compile(
    checkpointer=InMemorySaver()
)


# ==================================================
# PRUEBA DE APROBACION
# ==================================================

def probar_aprobacion(huella):

    print("\n=== PRUEBA DE APROBACION ===")

    config = {
        "configurable": {
            "thread_id": "despliegue-aprobacion-1"
        }
    }

    resultado = app_despliegue.invoke(
        {
            "huella_nueva": huella,
            "aprobado": False
        },
        config=config
    )

    assert "__interrupt__" in resultado

    pendiente = app_despliegue.get_state(config)

    print("Supervision pendiente:")
    print(pendiente.interrupts[0].value)

    resultado = app_despliegue.invoke(
        Command(resume=True),
        config=config
    )

    assert resultado["aprobado"] is True

    print("PRUEBA DE APROBACION: CORRECTA")


# ==================================================
# PRUEBA DE RECHAZO
# ==================================================

def probar_rechazo(huella):

    print("\n=== PRUEBA DE RECHAZO ===")

    config = {
        "configurable": {
            "thread_id": "despliegue-rechazo-1"
        }
    }

    resultado = app_despliegue.invoke(
        {
            "huella_nueva": huella,
            "aprobado": False
        },
        config=config
    )

    assert "__interrupt__" in resultado

    resultado = app_despliegue.invoke(
        Command(resume=False),
        config=config
    )

    assert resultado["aprobado"] is False

    print("PRUEBA DE RECHAZO: CORRECTA")


# ==================================================
# EJECUCION
# ==================================================

if __name__ == "__main__":

    # Huella de ejemplo.
    # Reemplazar por la huella obtenida en registro_prompts.py.

    huella = "ba2bcb4f4f13"

    probar_aprobacion(huella)
    probar_rechazo(huella)

    print("\nTODAS LAS PRUEBAS DE SUPERVISION CORRECTAS")
