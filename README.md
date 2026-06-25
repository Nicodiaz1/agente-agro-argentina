# 🌾 Agente Agro Argentina — Datos, IA y predicción del campo argentino

Una plataforma que **integra 4 fuentes de datos oficiales** sobre el agro argentino y permite explorarlas con un **agente de IA que responde en lenguaje natural**, un **modelo de Machine Learning** que predice el rinde y un **forecast de serie temporal**. Todo en una web interactiva.

Preguntas que el sistema puede responder:
- *"¿La sequía de 2008 explica la caída del rinde de soja en Santa Fe?"*
- *"¿Las retenciones movieron la siembra de soja hacia el maíz?"*
- *"¿Qué rinde esperar en Córdoba con tal nivel de lluvia y temperatura?"*

---

## 💡 Por qué nació este proyecto

Este proyecto nació de la necesidad de **aprender haciendo** y de **demostrar**, con algo real, que puedo llevar un problema de datos de punta a punta: desde conseguir y limpiar datos sucios del mundo real, hasta integrarlos, modelarlos y mostrarlos en un producto.

Soy **Agrónomo** reconvertido a **Data**, así que elegí un dominio donde mi conocimiento del negocio suma: la producción agrícola argentina. La idea era construir un **agente de IA (LLM)** sobre datos agropecuarios, y de ahí el proyecto fue creciendo capa por capa.

## 🧗 Los problemas que enfrenté (y cómo los resolví)

Ser honesto sobre las dificultades es parte del trabajo de un *data scientist* — el 80% del laburo es conseguir y limpiar los datos:

- **Quería hacer un LLM sobre un dataset, pero muchos datasets no existían o no servían.** Tuve que **evaluar y descartar fuentes** con criterio:
  - La **API del INA** (clima) solo tenía datos desde 2019 y en estaciones de ríos → no servía para series históricas. La descarté.
  - **SINAVIMO (plagas)** no tenía datos descargables ni serie temporal → descartada.
  - Los **precios del FMI** en datos.gob.ar estaban congelados en 2017 → los reemplacé por el **World Bank Pink Sheet** (sin empalmar metodologías distintas).
  - Las **retenciones** no tienen fuente abierta (viven en decretos y PDFs) → las **curé a mano por regímenes de política**, documentándolas como alícuotas anuales representativas.
- **El clima no venía a nivel provincia.** Lo resolví con la **NASA POWER API** (reanálisis satelital), tomando **múltiples coordenadas en zonas productivas** de cada provincia y promediándolas (no el centroide geográfico, para no sesgar con regiones de baja siembra).
- **Aprendí a interpretar resultados con honestidad:** que una correlación alta puede ser espuria por la tendencia, que el clima anual explica solo ~30% del rinde, y que una hipótesis (las retenciones) puede sostenerse o no según cómo se la mida.

## 📊 Fuentes de datos integradas

| Capa | Fuente | Cómo la conseguí |
|------|--------|------------------|
| **Producción** | Estimaciones Agrícolas (MAGyP / Bioeconomía) | CSV oficial, 1969–2024 (~160k registros), limpieza con pandas |
| **Clima** | NASA POWER API | API REST por coordenadas; 13 provincias × puntos productivos; precipitación, temperatura, radiación, humedad de suelo, viento |
| **Economía** | World Bank Pink Sheet + datos.gob.ar (API de series) | Precios internacionales (soja, maíz, trigo) + tipo de cambio |
| **Política** | Curado manual por regímenes | Alícuotas de retenciones por cultivo |

Las 4 fuentes se integran en una base **SQLite**, unidas por provincia y año.

## 🤖 Agente de IA (text-to-SQL)

```
Pregunta en español
   → [Claude] la traduce a SQL
   → el código ejecuta el SQL sobre SQLite (solo lectura)
   → [Claude] interpreta el resultado y genera un insight de negocio
```

- **Robusto:** manejo de errores para que nunca se caiga.
- **Seguro:** solo permite consultas `SELECT` (el LLM nunca puede modificar la base).
- Genera SQL avanzado solo: JOINs entre las 4 tablas, correlaciones, *window functions*.

## 🔮 Machine Learning

- **Modelo de rinde (RandomForest):** predice el rendimiento de soja a partir de clima + provincia + año. Resultado honesto: el clima anual provincial explica ~30% del rinde; el resto es manejo, genética y detalle intra-campaña no disponible a esta granularidad.
- **Análisis de retenciones (feature engineering):** se construye `precio_neto = precio × (1 − retención)` ("lo que le queda al productor") y se analiza, con cambios año a año (para sacar la tendencia), si las retenciones mueven la **sustitución soja↔maíz**.

## 📈 Serie temporal (forecasting)

Forecast del rinde de soja con **suavizado exponencial de Holt** (statsmodels). Proyecta la tendencia histórica a futuro. Se documenta la diferencia entre un forecast **univariado** (solo aprende de la serie) y uno **con variables exógenas** (ARIMAX), que incorporaría escenarios climáticos.

## 🛠️ Tecnologías

| Área | Herramientas |
|------|--------------|
| **Lenguaje** | Python |
| **Datos / ETL** | pandas, SQL, SQLite |
| **APIs REST** | NASA POWER, datos.gob.ar (Series de Tiempo), requests |
| **IA / LLM** | Claude API (Anthropic), prompt engineering, text-to-SQL |
| **Machine Learning** | scikit-learn (RandomForest), feature engineering |
| **Series temporales** | statsmodels (Exponential Smoothing / Holt) |
| **Web / Producto** | Streamlit |
| **Tooling** | Git, entornos virtuales (venv) |

## ▶️ Cómo correr

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=tu_key" > .env   # API key de Anthropic

python agente.py          # agente en la terminal
streamlit run app.py      # interfaz web (agente + ML + forecast)
```

## 📁 Estructura

```
app.py             # interfaz web (Streamlit): agente + predictor ML + forecast
agente.py          # agente text-to-SQL (programa de terminal)
esquema.py         # descripción de las tablas para el LLM
agro.db            # base SQLite con las 4 fuentes integradas
clima.ipynb        # ETL clima (NASA POWER API)
economia.ipynb     # ETL economía (precios + dólar + retenciones)
modelo.ipynb       # modelos de Machine Learning
serie_temporal.ipynb  # forecast de serie temporal
```

---

## 🙋 Sobre mí

Muchas gracias por leerme y por tomarte el tiempo de ver mi proyecto. 🌱

Soy **Nicolás Díaz**, un nuevo Junior Data Scientist con background en agronomia, aprendiendo un poco mas cada dia. Estoy **abierto a oportunidades laborales** en Data Science / Data Analytics para seguir aprendiendo y aportar mi grano de arena.

- 📧 **Email:** nicolasdiiaz0@gmail.com
- 📱 **Celular:** +54 351 211 8820

*Proyecto de portfolio — construido aprendiendo, equivocándome y resolviendo, que es como se aprende de verdad.*
