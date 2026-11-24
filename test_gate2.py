"""Pruebas de los cuatro criterios no compensables del Gate 2."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
SERVICE_PATH = ROOT / "Gate 2" / "servicio_rag.py"
SPEC = importlib.util.spec_from_file_location("gate2_service", SERVICE_PATH)
service = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(service)

SENSITIVE = "ana.perez@example.com"
QUESTION = f"¿Qué maquinaria nivela terreno? Contacto de prueba: {SENSITIVE}"


class FakeDocument:
    def __init__(self, text, source):
        self.page_content = text
        self.metadata = {"fuente": source}


class FakeStore:
    def similarity_search(self, question, k=3):
        return [FakeDocument("La motoniveladora se recomienda para nivelación.", "maquinaria")]


class FakeResponse:
    content = "La motoniveladora se recomienda para nivelación [1]."
    usage_metadata = {"input_tokens": 20, "output_tokens": 10}


class FakeChat:
    def __init__(self, **kwargs):
        pass

    def invoke(self, prompt):
        assert "maquinaria" in prompt
        return FakeResponse()


@pytest.fixture
def isolated_service(monkeypatch, tmp_path):
    monkeypatch.setattr(service, "HERE", tmp_path)
    monkeypatch.setattr(service, "open_index", lambda: (FakeStore(), "fake-key"))
    monkeypatch.setattr(
        service,
        "dependencies",
        lambda: (None, None, FakeChat, None, None, None, None, None, None, None),
    )
    monkeypatch.setenv("PRECIO_ENTRADA_MILLON_USD", "0.30")
    monkeypatch.setenv("PRECIO_SALIDA_MILLON_USD", "2.50")
    return tmp_path


def ejecutar_servicio(question=QUESTION):
    result = service.ask(question)
    return result["respuesta"], result["fuentes"]


def test_1_pipeline_sin_excepciones(isolated_service):
    answer, sources = ejecutar_servicio()
    assert answer.strip()
    assert sources


def test_2_respuesta_cita_fuente(isolated_service):
    answer, sources = ejecutar_servicio()
    assert "[1]" in answer
    assert any(source["cita"] in answer for source in sources)
    assert any(source["fuente"] == "maquinaria" for source in sources)


def test_3_logs_sin_contenido_crudo(isolated_service):
    ejecutar_servicio()
    logs = (isolated_service / "trazas.jsonl").read_text(encoding="utf-8")
    assert SENSITIVE not in logs
    assert QUESTION not in logs
    records = [json.loads(line) for line in logs.splitlines()]
    trace_ids = {record["trace_id"] for record in records}
    assert len(trace_ids) == 1 and "" not in trace_ids


def test_4_supervision_pausa_y_reanuda():
    from langgraph.types import Command

    app = service.build_approval_graph()
    config = {"configurable": {"thread_id": "test-gate2-approval"}}
    initial = {"prompt_hash": "testhash123", "approved": False}
    paused = app.invoke(initial, config=config)
    assert "__interrupt__" in paused
    resumed = app.invoke(Command(resume=True), config=config)
    assert "__interrupt__" not in resumed
    assert resumed["approved"] is True
