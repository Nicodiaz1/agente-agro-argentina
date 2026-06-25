import pandas as pd
import sqlite3
from agente import agente
import os
import streamlit as st

try:
    if "ANTHROPIC_API_KEY" in st.secrets:
        os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    pass

st.set_page_config(page_title="Agro Argentina IA", page_icon='🌾', layout="wide")

st.title("Agente Agro Argentina")
st.markdown(
    "Pregunta sobre **produccion, clima, economia y retenciones** "
    "del agro Argentino. Una IA traduce tu pregunta a SQL y te da el insight!!!"
)

st.divider()

pregunta = st.text_input(
    "Tu pregunta:",
    placeholder="Ej: Como se relaciono la lluvia con el rinde de soja en Santa Fe?"
)

if st.button("Preguntar") and pregunta:
    with st.spinner("Pensando..."):
        sql, resultado, insight = agente(pregunta)

        st.subheader("SQL generado")
        st.code(sql, language= "sql")

        st.subheader("Resultado!")
        st.dataframe(resultado, use_container_width=True)

        st.subheader("Insight!!!")
        st.markdown(insight)


#Ahora vamos con ML

from sklearn.ensemble import RandomForestRegressor

@st.cache_resource
def entrenar_modelo_soja():
    conn = sqlite3.connect("agro.db")
    df = pd.read_sql_query("""
        SELECT e.provincia, e.anio,
            SUM(e.produccion_tm)*1000.0/SUM(e.superficie_cosechada_ha) AS rendimiento,
            c.precip_total_mm, c.temp_media, c.temp_max_media,
            c.radiacion_solar, c.humedad_rel, c.viento, c.humedad_suelo
        FROM estimaciones e
        JOIN clima as c ON e.provincia=c.provincia AND e.anio=c.anio
        WHERE e.cultivo='soja total' AND e.superficie_cosechada_ha>0 AND e.produccion_tm>0
        GROUP BY e.provincia, e.anio              
    """, conn)
    conn.close()
    y = df["rendimiento"]
    X = pd.get_dummies(df.drop(columns=["rendimiento"]), columns=["provincia"])
    modelo = RandomForestRegressor(n_estimators=200, random_state=42)
    modelo.fit(X, y)
    return modelo, X.columns, df

st.divider()
st.header("🔮 Predictor de rinde de soja")
st.markdown("Move las variables y mira el rinde estimado por el modelo de ML")

modelo_ml, columnas_ml, df_ml = entrenar_modelo_soja()

col1, col2 = st.columns(2)
with col1:
    provincia = st.selectbox("provincia", sorted(df_ml["provincia"].unique()))
    anio = st.slider("Año", 2000, 2024, 2020)
    precip = st.slider("Lluvia anual (mm)", 400, 2000, 1100)
    temp = st.slider("Temp media (°C)", 14.0, 26.0, 18.0)
    temp_media_max = st.slider("Temp media máxima (°C)", 20.0, 32.0, 25.0)
with col2:
    radiacion = st.slider("Radiación solar", 14.0, 24.0, 18.0)
    humedad_rel = st.slider("Humedad relativa (%)", 50.0, 85.0, 70.0)
    viento = st.slider("Viento (m/s)", 1.0, 5.0, 3.0)
    humedad_suelo = st.slider("Humedad de suelo (0-1)", 0.3, 0.9, 0.6)

entrada = pd.DataFrame([{
    "anio": anio, "precip_total_mm": precip, "temp_media": temp,
    "temp_max_media": temp_media_max, "radiacion_solar": radiacion,
    "humedad_rel": humedad_rel, "viento": viento, "humedad_suelo": humedad_suelo,
    "provincia": provincia,
}])
entrada = pd.get_dummies(entrada, columns=["provincia"])
entrada = entrada.reindex(columns=columnas_ml, fill_value=0)

pred = modelo_ml.predict(entrada)[0]
st.metric("Rinde estimado de soja", f"{pred:,.0f} kg/ha")

from statsmodels.tsa.holtwinters import ExponentialSmoothing

@st.cache_data
def forecast_soja():
    conn = sqlite3.connect("agro.db")
    s = pd.read_sql_query("""
        SELECT anio, SUM(produccion_tm)*1000.0/SUM(superficie_cosechada_ha) AS rendimiento
        FROM estimaciones
        WHERE cultivo='soja total' AND superficie_cosechada_ha>0
        GROUP BY anio ORDER BY anio
    """, conn)
    conn.close()
    s = s.set_index("anio")["rendimiento"]
    fc = ExponentialSmoothing(s, trend="add", damped_trend=True).fit().forecast(5)
    combinado = pd.concat([s.rename("Histórico"), fc.rename("Forecast")], axis=1)
    return combinado, fc

st.divider()
st.header("📈 Forecast del rinde de soja (serie temporal)")
st.markdown(
    "Proyección de los próximos 5 años con suavizado exponencial (Holt). "
    "Aprende de la **tendencia histórica** (no del clima)."
)

combinado, fc = forecast_soja()
st.line_chart(combinado)
st.dataframe(fc.round(0).rename("Rinde proyectado (kg/ha)"))