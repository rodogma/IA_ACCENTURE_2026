# Límites de autonomía del agente de maquinaria y aprobaciones

**Proyecto:** IA_ACCENTURE_2026 — Módulo 2, Unidad 2.4 (Bloque 23)  
**Estado:** Documento de límites basado en el código compartido; verificación de trazas pendiente.

## 1. Herramientas y nivel de riesgo

| Herramienta | Archivo o actividad | Categoría | Riesgo | Justificación |
|---|---|---|---|---|
| `recomendar_maquinaria` | `bloque_21/actividad_agente.py` | Solo lectura | Bajo | Devuelve recomendaciones; no modifica sistemas externos. |
| `calcular_costo_arriendo` | `bloque_21/actividad_agente.py` | Solo lectura / cálculo | Bajo | Calcula una tarifa ficticia; no genera cobros ni contratos. |
| `escoger_maquinaria_segun_actividad` | `bloque_22/agente.py` | Solo lectura | Bajo | Consulta recomendaciones de equipos y no ejecuta acciones. |
| `generar_reembolso` | `bloque_23/aprobacion.py` | Escritura irreversible con impacto económico **si se conectara a pagos reales** | Alto por diseño de la acción | Un reembolso real afectaría dinero. La implementación actual solo simula el resultado y registra la aprobación en memoria; no mueve fondos. |

**Escritura reversible:** no se ha identificado una herramienta de esta categoría en el código compartido. No debe inventarse una para completar la tabla.

## 2. Aprobación humana

- **`generar_reembolso`: obligatoria antes de continuar.** La función `esperar_aprobacion` pide al supervisor presionar `S` o `N`, con un plazo máximo de 300 segundos. Si se rechaza o vence el plazo, no se autoriza la simulación del reembolso. La decisión queda en `registro_aprobaciones`, una lista en memoria.
- **Herramientas de recomendación y cálculo: no requieren aprobación previa**, porque no modifican datos ni ejecutan transacciones. Sus resultados deben presentarse como orientación y, en el caso de las tarifas, como ejemplos ficticios.
- **Regla para producción:** no conectar `generar_reembolso` a un servicio de pagos sin controles adicionales: identidad y permisos del aprobador, límites de monto, validación del pedido, registro persistente y prevención de ejecuciones duplicadas.

## 3. Revisión de trazas

**Frecuencia propuesta:** revisar todas las solicitudes de reembolso y sus decisiones al finalizar cada jornada de pruebas; revisar semanalmente las interacciones de solo lectura. Durante pruebas de integración, revisar cada ejecución.

**Qué buscar:**

1. Llamadas a `generar_reembolso` sin una aprobación explícita, con rechazo o con tiempo agotado.
2. Repeticiones de la misma solicitud (mismo pedido y monto), especialmente después de errores o reintentos.
3. Montos negativos, cero, anómalos o diferentes de los solicitados.
4. Herramientas elegidas fuera de contexto, argumentos incorrectos y respuestas que atribuyen acciones no realizadas.
5. Errores `503`, tiempos de espera, excepciones y consultas interrumpidas.
6. Diferencias entre la herramienta invocada, su observación y la respuesta final.

**Fuentes de evidencia:** `intermediate_steps` cuando el ejecutor los devuelve; `registro_aprobaciones` para la demostración de aprobación; `trazas_agente.jsonl` solo si existe y se ha conectado efectivamente un mecanismo de escritura de trazas. El código de aprobación compartido no escribe por sí solo ese archivo.

## 4. Respuesta ante comportamiento inesperado

1. **Detener la ejecución** y, si hay riesgo económico, deshabilitar temporalmente la herramienta afectada.
2. **Conservar evidencia:** fecha, sesión, entrada, argumentos, observación, respuesta, error y decisión humana, sin exponer claves API.
3. **Verificar el alcance:** determinar si fue una simulación, una recomendación incorrecta o una acción externa real.
4. **Revisar el código y el prompt:** comprobar descripción de la herramienta, esquema de argumentos, condiciones de aprobación y manejo de errores.
5. **Corregir y probar:** validar aprobación `S`, rechazo `N`, vencimiento de plazo, monto inválido y solicitudes repetidas.
6. **Rehabilitar solo después de comprobar los controles** y documentar la incidencia y la corrección.

## 5. Verificación contra el código real

Desde PowerShell, en la raíz del proyecto:

```powershell
Select-String -Path .\Modulo_2\bloque_23\aprobacion.py -Pattern 'esperar_aprobacion\('
```

Debe mostrar la definición de `esperar_aprobacion` y su llamada dentro de `generar_reembolso`.

Para comprobar las trazas, si el archivo existe en la raíz:

```powershell
Test-Path .\trazas_agente.jsonl
Get-Content .\trazas_agente.jsonl | Measure-Object -Line
Select-String -Path .\trazas_agente.jsonl -Pattern 'generar_reembolso'
```

Si `Test-Path` devuelve `False`, buscar el archivo en otra carpeta o implementar el registro antes de afirmar que hay trazas reales. **No crear registros ficticios para presentarlos como evidencia.**

## 6. Estado de cumplimiento

- **Clasificación por riesgo:** documentada.
- **Aprobación humana:** implementada en el ejemplo de `generar_reembolso`, según el código compartido; falta verificar una ejecución satisfactoria de la versión corregida en Windows.
- **Revisión de trazas:** política definida; existencia y contenido de `trazas_agente.jsonl` aún no verificados.
- **Plan de incidentes:** documentado.

**Conclusión:** este documento define los límites de autonomía y la supervisión del agente. La entrega quedará respaldada completamente cuando se compruebe la aprobación en ejecución y se adjunten trazas reales del agente.
