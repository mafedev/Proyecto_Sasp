# modelo.py (PARTE PREDICTIVA)
import pandas as pd
import numpy as np
from keras.models import load_model
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import MeanSquaredError

modelo = load_model("modelo_entrenado.h5", custom_objects={"mse": MeanSquaredError()})


# Cargar el DataFrame transpuesto (especies como columnas)
df_extintas = pd.read_csv("data/especies_extintas.csv", index_col=0).T

def predecir_nn(especie):
    if especie not in df_extintas.columns:
        return None

    poblacion = df_extintas[especie].fillna(0).values.reshape(1, -1)
    prediccion = modelo.predict(poblacion)
    return int(prediccion[0][0])