# Matriz de riesgos - asistente de maquinaria y construcción

Escala: probabilidad e impacto de 1 a 5. Puntaje = P x I. Crítico: 15-25; alto: 9-14; medio: 4-8; bajo: 1-3.

| Riesgo del caso | P | I | Nivel | Mitigación y punto de supervisión humana |
|---|---:|---:|---|---|
| Inyección de instrucciones dentro de un documento recuperado | 4 | 5 | CRÍTICO | El filtro descarta fragmentos sospechosos antes del prompt. El responsable del corpus revisa manualmente el documento marcado antes de reindexarlo. |
| Recomendación de maquinaria equivocada para una tarea de obra | 3 | 5 | ALTO | Respuesta basada en contexto citado y abstención sin evidencia. Un profesional de obra revisa respuesta y fuentes antes de usarla para una decisión operativa. |
| Documento desactualizado sobre maquinaria o procedimiento | 3 | 4 | ALTO | Revisar fecha y procedencia durante la actualización. El responsable del corpus aprueba la nueva versión antes de publicarla en el índice. |
| Recuperación de una fuente irrelevante para la consulta | 3 | 4 | ALTO | Evaluar precision/recall con los casos etiquetados de esta entrega. Una persona revisa los resultados antes de promover cambios de configuración. |
| Caída o latencia alta de Gemini | 3 | 3 | MEDIO | Registrar evento y latencia sin texto de consulta; el operador decide reintentar o informar indisponibilidad. |
| Exposición de preguntas o fragmentos privados en logs | 2 | 5 | ALTO | El logger admite solo longitudes, conteos, tokens, tiempos y trace_id. El responsable de seguridad inspecciona los registros antes de compartirlos. |

Todos los riesgos altos y críticos tienen una acción humana concreta y un responsable/punto de revisión definido.
