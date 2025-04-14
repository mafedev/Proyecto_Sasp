import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Prepara dataset de entrenamiento desde especies extintas
def preparar_dataset_entrenamiento(df_extintas):
    datos = []
    for especie in df_extintas.columns:
        y = pd.to_numeric(df_extintas[especie], errors="coerce")
        X = df_extintas.index.values.reshape(-1, 1)
        mask = ~np.isnan(y)
        if mask.sum() > 2:
            for xi, yi in zip(X[mask], y[mask]):
                datos.append({"año": xi[0], "poblacion": yi, "especie": especie})
    return pd.DataFrame(datos)

# Entrena un modelo de regresión general
def entrenar_modelo_general(df_extintas):
    df_train = preparar_dataset_entrenamiento(df_extintas)
    X = df_train["año"].values.reshape(-1, 1)
    y = df_train["poblacion"]
    modelo = LinearRegression()
    modelo.fit(X, y)
    return modelo

# Aplica ese modelo a una especie en peligro actual
def predecir_extincion_especie(df_actuales, especie, modelo):
    y = pd.to_numeric(df_actuales[especie], errors="coerce")
    X = df_actuales.index.values.reshape(-1, 1)
    mask = ~np.isnan(y)
    if mask.sum() < 2:
        return None, None

    # Usa pendiente del modelo global, pero ajusta la intersección
    pendiente = modelo.coef_[0]
    intercepto = np.mean(y[mask]) - pendiente * np.mean(X[mask])
    if pendiente == 0:
        return None, None

    año_ext = -intercepto / pendiente

    # Gráfico
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.scatter(X[mask], y[mask], color='orange', label='Datos reales')
    y_pred = pendiente * X + intercepto
    ax.plot(X, y_pred, linestyle="--", color="blue", label="Predicción IA")
    ax.set_title(f"Evolución poblacional de {especie}")
    ax.set_xlabel("Año")
    ax.set_ylabel("Población estimada")
    ax.grid()
    ax.legend()

    # Convertir a base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_b64 = base64.b64encode(buffer.read()).decode("utf-8")
    plt.close()

    return int(año_ext), img_b64