from flask import Flask, render_template, request
from utils.funciones import (
    cargar_datos,
    predecir_año_extincion,
    buscar_en_gbif,
    crear_mapa_html
)
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = Flask(__name__)

# Datos estructurados para monitorización
df_monitor = cargar_datos("data/especies_en_peligro.csv")
especies_monitor = df_monitor.columns.tolist()

# ----------------------------
# PÁGINAS ESTÁTICAS
# ----------------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/blog")
def blog():
    return render_template("blog.html")

@app.route("/casos_exito")
def casos_exito():
    return render_template("casos_exito.html")

@app.route("/galeria")
def galeria():
    return render_template("galeria.html")

@app.route("/huella_carbono", methods=["GET", "POST"])
def huella_carbono():
    return render_template("huella_carbono.html")

@app.route("/huella_persona")
def huella_persona():
    return render_template("huella_persona.html")

@app.route("/huella_empresa")
def huella_empresa():
    return render_template("huella_empresa.html")

@app.route("/ayudar")
def acciones():
    return render_template("ayudar.html")

@app.route("/refugios")
def refugios():
    return render_template("refugios.html")

# Datos dispersos estilo Excel
df_disperso = pd.read_excel("data/especies_extintas.xlsx")
columna_especie = df_disperso.columns[0]
años_excel = pd.to_numeric(df_disperso.columns[1:], errors="coerce").dropna().astype(int)

# ------------------ MONITORIZACIÓN IA ------------------
@app.route("/monitorizar", methods=["GET", "POST"])
def monitorizar():
    especie = request.form.get("especie") or especies_monitor[0]
    año_pred, grafico_b64 = predecir_año_extincion(df_monitor, especie)
    observaciones = buscar_en_gbif(especie)
    mapa_html = crear_mapa_html(observaciones)

    return render_template("monitorizar.html",
                           especies=especies_monitor,
                           especie=especie,
                           año_pred=año_pred,
                           grafico=grafico_b64,
                           mapa=mapa_html)

# ------------------ EXPLORADOR DE ESPECIES ------------------
@app.route("/especies", methods=["GET", "POST"])
def especies():
    especie = request.form.get("especie")
    datos_especie = None
    mapa_html = None
    grafico_b64 = None
    año_ext = None

    if especie:
        registros = buscar_en_gbif(especie)
        datos_especie = registros[:50] if registros else []

        df_fila = df_disperso[df_disperso[columna_especie] == especie]
        if not df_fila.empty:
            fila = df_fila.iloc[0]
            y = pd.to_numeric(fila[1:].values, errors="coerce")
            X = años_excel.values.reshape(-1, 1)
            mask = ~np.isnan(y)

            if mask.sum() >= 2:
                modelo = LinearRegression().fit(X[mask], y[mask])
                año_ext = -modelo.intercept_ / modelo.coef_[0] if modelo.coef_[0] != 0 else None

                fig, ax = plt.subplots(figsize=(8, 4))
                ax.scatter(años_excel, y, color='orange', label=especie)
                ax.plot(años_excel, modelo.predict(X), linestyle="--", color="blue")
                ax.set_xlabel("Año")
                ax.set_ylabel("Población")
                ax.set_title("Evolución poblacional")
                ax.grid()
                ax.legend()

                buf = BytesIO()
                fig.savefig(buf, format="png")
                buf.seek(0)
                grafico_b64 = base64.b64encode(buf.read()).decode("utf-8")
                plt.close(fig)

            mapa_html = crear_mapa_html(registros)

    return render_template("especies.html",
                           especie=especie,
                           año_pred=año_ext,
                           grafico=grafico_b64,
                           mapa=mapa_html,
                           datos=datos_especie)

if __name__ == "__main__":
    app.run(debug=True)