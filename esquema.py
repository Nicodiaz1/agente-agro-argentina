ESQUEMA = """
Tabla: estimaciones
Columnas:
- cultivo (texto): nombre del cultivo, ej 'soja total', 'maíz', 'trigo total'
- anio (entero): año de la campaña, de 1969 a 2024
- campania (texto): ej '2020/2021'
- provincia (texto): nombre de la provincia
- provincia_id (texto): código INDEC, ej '06'
- departamento (texto): nombre del departamento
- departamento_id (texto): código INDEC, ej '06854'
- superficie_sembrada_ha (entero): hectáreas sembradas
- superficie_cosechada_ha (entero): hectáreas cosechadas
- produccion_tm (entero): producción en toneladas
- rendimiento_kgxha (entero): rendimiento en kg por hectárea

Tabla: clima
Columnas:
- anio (entero): año, de 2000 a 2024
- provincia (texto): nombre de la provincia (coincide con estimaciones.provincia)
- precip_total_mm (decimal): precipitación total anual en milímetros
- temp_media (decimal): temperatura media anual en °C
- temp_max_media (decimal): temperatura máxima media anual en °C (indicador de golpe de calor)
- radiacion_solar (decimal): radiación solar media (MJ/m²/día), energía para el cultivo
- humedad_rel (decimal): humedad relativa media anual en %
- viento (decimal): velocidad media del viento (m/s)
- humedad_suelo (decimal): humedad del suelo en zona radicular (0 a 1, donde 1 es saturado)

IMPORTANTE: para relacionar producción con clima, unir (JOIN) las tablas
estimaciones y clima por provincia Y anio.
Nota: la tabla clima solo cubre los años 2000-2024 y 13 provincias principales.

Tabla: economia
Datos económicos NACIONALES por año (no por provincia).
Columnas:
- anio (entero): año, de 2000 a 2026
- precio_soja (decimal): precio internacional de la soja en US$/tonelada
- precio_maiz (decimal): precio internacional del maíz en US$/tonelada
- precio_trigo (decimal): precio internacional del trigo en US$/tonelada
- tipo_cambio_prom (decimal): tipo de cambio peso/dólar promedio anual (desde 2014)

IMPORTANTE: para relacionar con producción, unir (JOIN) estimaciones y economia por anio.
Es nivel NACIONAL (no tiene provincia). Para precios, usar la columna del cultivo
correspondiente (precio_soja para soja, precio_maiz para maíz, precio_trigo para trigo).
Nota: precios cubren 2000-2025; tipo de cambio desde 2014.

Tabla: retenciones
Alícuotas de derechos de exportación (retenciones) NACIONALES por año, en %.
Columnas:
- anio (entero): año, de 2000 a 2024
- retencion_soja (decimal): % de retención a la soja
- retencion_maiz (decimal): % de retención al maíz
- retencion_trigo (decimal): % de retención al trigo

IMPORTANTE: unir (JOIN) con estimaciones por anio. Es nivel NACIONAL.
Para cada cultivo usar su columna (retencion_soja para soja, etc.).
"""