# Obtener los mismos años (columnas) usados en el entrenamiento
# Se asume que están en "scaler.save"
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import MeanSquaredError
import joblib

modelo = load_model("modelo_entrenado.h5", custom_objects={"mse": MeanSquaredError()})
scaler = joblib.load("scaler.save")

df_monitor = pd.read_csv("data/especies_en_peligro.csv", index_col=0)

# Obtener los años (features) que usó el scaler
n_features = scaler.mean_.shape[0]

def predecir_nn(especie):
    try:
        if especie not in df_monitor.columns:
            print(f"La especie '{especie}' no está en el DataFrame de monitoreo.")
            return None

        # Obtener solo los primeros n años (las mismas columnas que se usaron en entrenamiento)
        serie = df_monitor[especie].fillna(0).values[:n_features].reshape(1, -1)

        if serie.shape[1] != n_features:
            print(f"La especie '{especie}' tiene {serie.shape[1]} años, se requieren {n_features}.")
            return None

        serie_escalada = scaler.transform(serie)
        prediccion = modelo.predict(serie_escalada)
        probabilidad = float(prediccion[0][0])
        return probabilidad

    except Exception as e:
        print(f"Error en predecir_nn: {e}")
        return None

def obtener_df_extintas():
    return df_monitor
