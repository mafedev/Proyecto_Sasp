from flask import Flask, render_template, request
from utils.funciones import cargar_datos, buscar_en_gbif, crear_mapa_html, predecir_año_extincion

# Inicializa la aplicación Flask
app = Flask(__name__)


@app.route("/") # Indica que es la ruta raíz
def index():
    return render_template("index.html") # Se devuelve la plantilla index.html

# Secciones del sitio
@app.route("/blog")
def blog():
    return render_template("blog.html")

@app.route("/acciones")
def acciones():
    return render_template("ayudar.html")

@app.route("/casos-exito")
def casos_exito():
    return render_template("casos_exito.html")

@app.route("/galeria")
def galeria():
    return render_template("galeria.html")

@app.route("/huella-carbono", methods=["GET", "POST"])
def huella_carbono():
    return render_template("huella_carbono.html")

# MONITORIZAR ESPECIES
@app.route("/monitorizar", methods=["GET", "POST"])
def monitorizar():
    df = cargar_datos("data/especies_en_peligro.csv")
    especies = df.columns.tolist()
    especie = request.form.get("especie") or especies[0]

    registros = buscar_en_gbif(especie)
    mapa_html = crear_mapa_html(registros)
    año_pred, grafico = predecir_año_extincion(df, especie)

    return render_template("monitorizar.html",
                           especies=especies,
                           especie=especie,
                           registros=registros,
                           mapa_html=mapa_html,
                           año_pred=año_pred,
                           plot_img=grafico)

# Vista individual por especie
@app.route("/especie/<nombre_especie>")
def detalle_especie(nombre_especie):
    df = cargar_datos("data/especies_en_peligro.csv")
    especies = df.columns.tolist()
    if nombre_especie not in especies:
        return "Especie no encontrada", 404

    registros = buscar_en_gbif(nombre_especie)
    mapa_html = crear_mapa_html(registros)
    año_pred, grafico = predecir_año_extincion(df, nombre_especie)

    return render_template("especie_detalle.html",
                           especie=nombre_especie,
                           mapa_html=mapa_html,
                           año_pred=año_pred,
                           plot_img=grafico,
                           registros=registros)

if __name__ == "__main__":
    app.run(debug=True) # Se corre la app en modo debug para ver errores y cambios en tiempo real

@app.route("/especies")
def especies():
    df = cargar_datos("data/especies_en_peligro.csv")
    especies = df.columns.tolist()
    return render_template("especies.html", especies=especies)
