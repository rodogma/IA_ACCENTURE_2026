"""Tres prompts reproducibles para una miniaplicación que procesa consultas de texto."""
BANCO_DE_PROMPTS = [
    {
        'nombre': 'clasificar_sentimiento',
        'system_instruction': (
            'Eres un clasificador de opiniones en español. Responde exclusivamente un objeto JSON. '
            'Clasifica el mensaje en positivo, negativo o neutro. '
            'Incluye confianza numérica entre 0 y 1. No incluyas texto adicional.'
        ),
        'ejemplo_usuario': 'La atención fue rápida y muy amable.',
        'claves_esperadas': {'sentimiento': str, 'confianza': float},
        'response_schema': {
            'type': 'OBJECT',
            'properties': {
                'sentimiento': {'type': 'STRING', 'enum': ['positivo', 'negativo', 'neutro']},
                'confianza': {'type': 'NUMBER'},
            },
            'required': ['sentimiento', 'confianza'],
        },
    },
    {
        'nombre': 'extraer_entidades',
        'system_instruction': (
            'Extrae los nombres de lugares explícitamente mencionados en el texto. '
            'Responde exclusivamente un objeto JSON con una clave lugares que contenga '
            'una lista de cadenas. No inventes lugares ni agregues explicaciones.'
        ),
        'ejemplo_usuario': 'Viajé desde Santiago hasta Valparaíso y luego visité Viña del Mar.',
        'claves_esperadas': {'lugares': list},
        'response_schema': {
            'type': 'OBJECT',
            'properties': {'lugares': {'type': 'ARRAY', 'items': {'type': 'STRING'}}},
            'required': ['lugares'],
        },
    },
    {
        'nombre': 'resumen_corto',
        'system_instruction': (
            'Resume el texto en español en una sola oración clara. '
            'Responde exclusivamente un objeto JSON con la clave resumen, '
            'cuyo valor sea una cadena de texto. No agregues información no mencionada.'
        ),
        'ejemplo_usuario': (
            'El equipo revisó los documentos durante la mañana. '
            'Identificó dos observaciones y acordó corregirlas antes del viernes.'
        ),
        'claves_esperadas': {'resumen': str},
        'response_schema': {
            'type': 'OBJECT',
            'properties': {'resumen': {'type': 'STRING'}},
            'required': ['resumen'],
        },
    },
]
