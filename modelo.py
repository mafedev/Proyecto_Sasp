import os
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping

# Parámetros
tamaño_imagen = (150, 150)
lote = 16
épocas = 15

# Aumentación de datos
generador_imagenes = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.2
)

# Cargar datos
ruta_datos = "data/animals"
entrenamiento = generador_imagenes.flow_from_directory(
    ruta_datos,
    target_size=tamaño_imagen,
    batch_size=lote,
    class_mode='categorical',
    subset='training'
)

validacion = generador_imagenes.flow_from_directory(
    ruta_datos,
    target_size=tamaño_imagen,
    batch_size=lote,
    class_mode='categorical',
    subset='validation'
)

# Modelo
modelo = models.Sequential([
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(150, 150, 3
