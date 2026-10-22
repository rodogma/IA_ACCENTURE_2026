# Actividad Prompt — banco de prompts y consistencia

Contiene tres prompts (sentimiento, entidades, resumen), el cliente Gemini extendido y un script para ejecutar 3 pruebas reales por prompt.

## Ubicación
Copiar `Modulo_1` y `prompts/` a la raíz del repositorio `IA_ACCENTURE_2026`. No elimines ni reemplaces los archivos de tus bloques anteriores; `cliente_gemini.py` es una variante aislada compatible con esta práctica.

## Ejecución
Desde la raíz del repositorio, con `.env` configurado con `GEMINI_API_KEY` y `requests` / `python-dotenv` instalados:

```powershell
python .\Modulo_1\probar_consistencia.py
```

El archivo `prompts/registro_resultados.json` se crea **solo después** de ejecutar el script contra la API real; no se incluye un registro ficticio en la entrega.

## Interpretación
Para cada prompt se cuenta la cantidad de respuestas que sean JSON válido y cumplan el tipo y las claves esperadas. No mide exactitud semántica de las respuestas. Problemas de red/cuota cuentan como fallos de la ejecución y quedan registrados con su motivo.

## Commit
```powershell
git add Modulo_1 prompts/banco_prompts.py prompts/registro_resultados.json
git commit -m "Agregar banco de prompts y validar consistencia"
git push origin <nombre-de-tu-rama>
```
