# Autoevaluacion final Gate 2

Completa los puntajes con una estimacion honesta de 0 a 100. El minimo de aprobacion indicado por la pauta es 80, pero el evaluador asigna su propia nota.

| Dimension | Peso | Autoevaluacion | Evidencia |
|---|---:|---:|---|
| Pipeline funcional | 25% | 90 | Corrida real guardada en `evidencias_corridas.jsonl`; cuatro pruebas en `test_gate2.py`. |
| Recuperacion y citacion | 15% | 85 | `resultados_metricas.json`; @1 perfecto en cinco casos y @3 reportado sin ocultar ruido. |
| Costo y latencia | 10% | 90 | Corrida con tokens, costo calculado y latencia en `evidencias_corridas.jsonl`. |
| Personalizacion | 15% | 90 | `decision_personalizacion.md`, comparacion para el caso propio. |
| Observabilidad | 15% | 90 | `trazas.jsonl`, trace_id y registro de consumo. |
| Seguridad y gobernanza | 20% | 90 | Filtro, aprobacion humana, `matriz_riesgos.md` y pruebas automatizadas. |

Calculo: `0.25*pipeline + 0.15*recuperacion + 0.10*costo + 0.15*personalizacion + 0.15*observabilidad + 0.20*seguridad`.

Estimacion actual: `88.5/100`. Es autoevaluacion del estudiante, no una nota oficial ni una garantia de resultado; ajustala si tu juicio sobre la evidencia difiere.

## Criterios no compensables

- Pipeline termina sin excepcion: evidencia de corrida real y test 1.
- Respuesta cita fuente: evidencia real y test 2.
- Logs sin pregunta o PII: test 3; las respuestas con contenido se conservan en evidencia separada, no en `trazas.jsonl`.
- Supervision humana pausa y reanuda: aprobacion real en `supervision_humana.jsonl` y test 4.

## Instalacion limpia y entrega

Desde la raiz, en Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python ".\Gate 2\servicio_rag.py" --pregunta "¿Que maquinaria recomienda el corpus para nivelar un terreno?"
python ".\Gate 2\servicio_rag.py" --evaluar
python ".\Gate 2\servicio_rag.py" --verificar-filtro
python ".\Gate 2\servicio_rag.py" --supervisar
python -m pytest -q test_gate2.py
git status --short
```

Configura `.env` localmente antes de la consulta real y no lo agregues al commit. Comprueba que el indice persistido del Bloque 24 exista y tenga documentos. Revisa los cambios antes de crear el commit de entrega.

El comando de pytest se ejecuta desde la raiz y valida la suite propia de Gate 2. Las pruebas historicas de otros bloques pueden requerir ejecutarse desde sus carpetas porque usan imports locales; no se consideran parte de esta verificacion.
