import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import BinaryCrossentropy
import joblib

# Cargar modelo y scaler
modelo = load_model("modelo_entrenado.h5", custom_objects={"binary_crossentropy": BinaryCrossentropy()})
scaler = joblib.load("scaler.save")

# Cargar el DataFrame de especies en peligro
df_monitor = pd.read_csv("data/especies_en_peligro.csv", index_col=0)

# Obtener cantidad de años (features) usados originalmente (sin contar la pendiente)
n_features_sin_pendiente = scaler.mean_.shape[0] - 1

def calcular_pendiente_ultimos_anios(valores, n=10):
    ultimos = valores[-n:]  # Últimos n valores
    x = np.arange(len(ultimos))
    y = ultimos
    if len(y) < 2 or np.all(y == y[0]):
        return 0  # Sin tendencia o con datos planos
    x_mean, y_mean = np.mean(x), np.mean(y)
    pendiente = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2)
    return pendiente

def predecir_nn(especie):
    try:
        if especie not in df_monitor.columns:
            print(f"La especie '{especie}' no está en el DataFrame.")
            return None

        # Obtener valores de población y limitar a n años esperados
        valores = df_monitor[especie].fillna(0).values[:n_features_sin_pendiente]

        # Validación
        if len(valores) < n_features_sin_pendiente:
            print(f"La especie '{especie}' no tiene suficientes años. Esperados: {n_features_sin_pendiente}")
            return None

        # Calcular la pendiente y agregarla como último valor
        pendiente = calcular_pendiente_ultimos_anios(valores)
        entrada = np.append(valores, pendiente).reshape(1, -1)

        # Escalar y predecir
        entrada_escalada = scaler.transform(entrada)
        prediccion = modelo.predict(entrada_escalada)
        probabilidad = float(prediccion[0][0])
        return probabilidad

    except Exception as e:
        print(f"Error en predecir_nn: {e}")
        return None

def obtener_df_extintas():
    return df_monitor