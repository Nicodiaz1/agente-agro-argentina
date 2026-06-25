import os
import sqlite3

import pandas as pd
from dotenv import load_dotenv
from anthropic import Anthropic

from esquema import ESQUEMA


#Configuramos!

load_dotenv()
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODELO = "claude-sonnet-4-6"
DB = "agro.db"

# Creamos las funciones!

def limpiar_sql(texto):
    texto = texto.strip()
    texto = texto.replace("```sql", "").replace("```", "")
    return texto.strip()

def pregunta_a_sql(pregunta):
    prompt = f"""Sos un experto en SQL (SQLite). Tengo esta tabla:
{ESQUEMA}

Escribí UNA consulta sql que responda: {pregunta}
Devolve SOLO el SQL, sin explicaciones ni formato markdown."""
    
    respuesta=client.messages.create(
        model=MODELO,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return limpiar_sql(respuesta.content[0].text)


def ejecutar_sql(sql):
    if not sql.strip().lower().startswith("select"):
        raise ValueError("Solo se permiten consultas SELECT(de lectura).")
    conn = sqlite3.connect(DB)
    resultado = pd.read_sql_query(sql,conn)
    conn.close()
    return resultado

def explicar_resultado(pregunta, resultado):
    prompt = f"""Sos un analista de datos del sector agropecuario argentino.

Un usuario preguntó: "{pregunta}"

La consulta devolvio estos datos:
{resultado.to_string(index=False)}

Escribí un insight breve (2-3 frases) que interprete el resultado en lenguaje claro, destacando lo relevante
para quien toma decisiones. No repitas números sin explicarlos."""
    
    respuesta = client.messages.create(
        model = MODELO,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return respuesta.content[0].text


def agente(pregunta):
    sql = pregunta_a_sql(pregunta)
    resultado = ejecutar_sql(sql)
    insight = explicar_resultado (pregunta, resultado)
    return sql, resultado, insight


# Creamos el programa principal

def main():
    print("Agente Agro Argentina - preguntá sobre produccion agricola (1969-2024)")
    print(" Escribí 'salir' para terminar.\n")

    while True:
        pregunta = input("\n Preguntá algo:")

        if pregunta.lower() == "salir":
            print("Chau gracias por tu consulta!")
            break
        
        try:
            sql, resultado, insight = agente(pregunta)
            print("\n Se ha generado el SQL")
            print(sql)
            print("\n Resultado generado")
            print(resultado.to_string(index=False))
            print("\n Se ha generado un Insight!!!")
            print(insight)
        except Exception as e:
            print(f"\n Algo fallo con esa pregunta: {e}")
            print("Proba reformularla")

if __name__ == "__main__": #Lo uso para que el archivo funcione tanto como programa ejecutable como modulo importable.
    main()