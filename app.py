from flask import Flask, render_template, request
import pandas as pd


# Estas funciones vienen del archivo funciones.py
from utils.funciones import (
    buscar_en_gbif,
    crear_mapa_html,
)

# Estas funciones vienen del archivo modelo_general.py
from utils.modelo_general import (
    entrenar_modelo_general,
    predecir_extincion_especie,
)

# Inicializa la aplicación Flask
app = Flask(__name__)


def cargar_datos(ruta_csv):
    import pandas as pd
    df = pd.read_csv(ruta_csv)
    print(f"Columnas en {ruta_csv}: {df.columns.tolist()}")
    return df


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

@app.route("/casos_exito")
def casos_exito():
    return render_template("casos_exito.html")

@app.route("/galeria")
def galeria():
    return render_template("galeria.html")

@app.route("/huella_carbono", methods=["GET", "POST"])
def huella_carbono():
    return render_template("huella_carbono.html")

# MONITORIZAR ESPECIES
@app.route("/monitorizar", methods=["GET", "POST"])
def monitorizar():
    # Cargamos ambos CSV
    df_actuales = pd.read_csv("data/especies_en_peligro.csv")
    #print("Columnas en df_actuales:", df_actuales.columns.tolist())  # Depuración
    #return "Revisando columnas en consola"
    #df_actuales.columns = ['Especies'] + list(range(-100, 1, 3))  # Ajusta según los años reales
    #df_extintas = cargar_datos("data/especies_extintas.csv")

    # Ajusta los nombres de las columnas
    num_years = len(df_actuales.columns) - 1  # Resta 1 para la columna 'Especies'
    df_actuales.columns = ['Especies'] + list(range(-100, -100 + num_years * 3, 3))  # Ajusta el rango según los años reales

    print("Columnas ajustadas en df_actuales:", df_actuales.columns.tolist())  # Depuración
    return "Columnas ajustadas correctamente"

    # Verifica las columnas disponibles
    print("Columnas en df_actuales:", df_actuales.columns)
    print("Columnas en df_extintas:", df_extintas.columns)

    # Ajusta el código para usar las columnas correctas
    especies = df_actuales['Especies'].tolist()  # Cambia según el nombre correcto
    especie = request.form.get("especie") or especies[0]

    # Entrenamos modelo IA con especies extintas
    modelo_ia = entrenar_modelo_general(df_extintas)

    # Aplicamos modelo IA a especie actual
    año_pred, grafico = predecir_extincion_especie(df_actuales, especie, modelo_ia)

    # Mapa y registros
    registros = buscar_en_gbif(especie)
    mapa_html = crear_mapa_html(registros)

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
    # Carga especies actuales
    df = cargar_datos("data/especies_en_peligro.csv")
    especies = df.columns.tolist()
    
    if nombre_especie not in especies:
        return "Especie no encontrada", 404

    # Entrena modelo IA con especies extintas
    df_extintas = cargar_datos("data/especies_extintas.csv")
    modelo_ia = entrenar_modelo_general(df_extintas)

    # Predicción para la especie actual
    año_pred, grafico = predecir_extincion_especie(df, nombre_especie, modelo_ia)

    # Buscar registros y generar el mapa
    registros = buscar_en_gbif(nombre_especie)
    mapa_html = crear_mapa_html(registros)

    # Mostrar plantilla HTML
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