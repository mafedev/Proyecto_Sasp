from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import requests
import folium
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import base64
from io import BytesIO

app = Flask(__name__)

# ---------------------- FUNCIONES ----------------------

def cargar_datos(nombre_archivo):
    df = pd.read_csv(nombre_archivo)
    df.set_index("Año", inplace=True)
    return df

def cargar_datos_extintos(nombre_archivo):
    df = pd.read_csv(nombre_archivo, index_col=0).T
    df.index = df.index.astype(int)
    return df

def buscar_en_gbif(nombre_especie):
    url = f"https://api.gbif.org/v1/occurrence/search?scientificName={nombre_especie}&limit=50"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json().get("results", [])
    return []

def crear_mapa_html(observaciones):
    m = folium.Map(location=[0, 0], zoom_start=2)
    for obs in observaciones:
        lat = obs.get("decimalLatitude")
        lon = obs.get("decimalLongitude")
        if lat and lon:
            folium.Marker(location=[lat, lon], popup=obs.get("country", "Observación")).add_to(m)
    return m._repr_html_()

def predecir_año_extincion(df, especie_objetivo):
    X = df.index.values.reshape(-1, 1)
    y = pd.to_numeric(df[especie_objetivo], errors="coerce")

    mask = ~np.isnan(y)
    if mask.sum() < 2:
        return None, None

    model = LinearRegression().fit(X[mask], y[mask])
    año_ext = -model.intercept_ / model.coef_[0] if model.coef_[0] != 0 else None

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.scatter(df.index, y, color='orange', label=especie_objetivo)
    if año_ext:
        y_pred = model.predict(X)
        ax.plot(df.index, y_pred, linestyle="--", color="blue", label="Tendencia")
        ax.legend()
        ax.set_xlabel("Año")
        ax.set_ylabel("Población estimada")
        ax.grid()

    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)

    return int(año_ext) if año_ext else None, img_b64

# ---------------------- CARGA DE DATOS ----------------------

df_monitor = cargar_datos("data/especies_en_peligro.csv")
especies_monitor = df_monitor.columns.tolist()

df_disperso = pd.read_excel("data/especies_extintas.xlsx")
columna_especie = df_disperso.columns[0]
años_excel = pd.to_numeric(df_disperso.columns[1:], errors="coerce").dropna().astype(int)

info_especies = pd.read_csv("data/info_especies.csv")  # ← contiene imagen, nombre, poblacion, estado, etc.

# ---------------------- RUTAS FLASK ----------------------

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

@app.route("/monitorizar", methods=["GET", "POST"])
def monitorizar():
    especie_seleccionada = request.form.get("especie") or especies_monitor[0]
    año_pred, grafico_b64 = predecir_año_extincion(df_monitor, especie_seleccionada)
    observaciones = buscar_en_gbif(especie_seleccionada)
    mapa_html = crear_mapa_html(observaciones)

    # Pasar info de las especies como "cards"
    cards = info_especies.to_dict(orient="records")

    return render_template("monitorizar.html",
                           especies=cards,
                           especie=especie_seleccionada,
                           año_pred=año_pred,
                           grafico=grafico_b64,
                           mapa=mapa_html)

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

@app.route("/estadisticas/<nombre>")
def estadisticas(nombre):
    if nombre not in df_monitor.columns:
        return f"No hay datos para '{nombre}'", 404

    año_pred, grafico_b64 = predecir_año_extincion(df_monitor, nombre)
    registros = buscar_en_gbif(nombre)
    mapa_html = crear_mapa_html(registros)

    return render_template("estadisticas.html",
                           especie=nombre,
                           año_pred=año_pred,
                           grafico=grafico_b64,
                           mapa=mapa_html)


# ---------------------- RUN ----------------------

if __name__ == "__main__":
    app.run(debug=True)
