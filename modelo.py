import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import BinaryCrossentropy
import joblib

# Cargar modelo y scaler previamente entrenados
modelo = load_model("modelos/modelo_entrenado.h5", custom_objects={"binary_crossentropy": BinaryCrossentropy()})
scaler = joblib.load("modelos/scaler.save")

# Cargar el DataFrame de monitoreo
df_monitor = pd.read_csv("data/especies_en_peligro.csv", index_col=0)
df_monitor = df_monitor.sort_index()  # Asegurarse de que los años estén en orden

# Determinar el número de features originales (sin contar la pendiente)
n_features_sin_pendiente = scaler.mean_.shape[0] - 1

def calcular_pendiente_ultimos_anios(valores, n=10):
    ultimos = valores[-n:]
    x = np.arange(len(ultimos))
    y = ultimos
    if len(y) < 2 or np.all(y == y[0]):
        return 0.0
    x_mean, y_mean = np.mean(x), np.mean(y)
    pendiente = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2)
    return pendiente

def predecir_nn(nombre_especie):
    try:
        if nombre_especie not in df_monitor.columns:
            print(f"La especie '{nombre_especie}' no está en el DataFrame.")
            return None

        valores_crudos = df_monitor[nombre_especie].fillna(0).values

        # Validar tamaño
        if len(valores_crudos) < n_features_sin_pendiente:
            print(f"La especie '{nombre_especie}' no tiene suficientes datos históricos. Esperados: {n_features_sin_pendiente}")
            return None

        valores = valores_crudos[:n_features_sin_pendiente]
        pendiente = calcular_pendiente_ultimos_anios(valores)

        entrada = np.append(valores, pendiente).reshape(1, -1)
        entrada_escalada = scaler.transform(entrada)

        prediccion = modelo.predict(entrada_escalada)
        return float(prediccion[0][0])

    except Exception as e:
        print(f"Error en predecir_nn: {e}")
        return None

def obtener_df_extintas():
    return df_monitor