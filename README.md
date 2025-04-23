# Monitoreo de especies en peligro de extinción

Aplicación web interactiva para el monitoreo, predicción y análisis de especies en peligro de extinción, construida con Flask, Jinja, Bootstrap 5 e inteligencia artificial.

---

## Tabla de Contenidos

- [Descripción](#descripción)  
- [Tecnologías](#tecnologías)  
- [Instalación](#instalación)  
- [Uso](#uso)  
- [Estructura del proyecto](#estructura-del-proyecto)
- [Integrantes](#integrantes)

---

## Descripción

**N-World** es una aplicación web que combina datos históricos con modelos de inteligencia artificial para predecir la probabilidad de extinción de especies amenazadas.

Características principales:

- Visualización de datos de población histórica por especie.
- Predicción de riesgo de extinción mediante regresión lineal o red neuronal.
- Mapas de distribución geográfica con datos de GBIF e iNaturalist.
- Información detallada sobre hábitat, amenazas, acciones recomendadas y organizaciones.
- Interfaz amigable y educativa con enfoque en sostenibilidad y conservación.

---

## Tecnologías

- Python 3.10+
- Flask
- TensorFlow / Keras
- Scikit-learn
- Pandas / NumPy
- Matplotlib
- Folium
- Bootstrap 5
- Jinja2

---

## Instalación

1. Clona el repositorio:

   ```bash
   git clone https://github.com/mafedev/Proyecto_Sasp.git
   cd Proyecto_Sasp

## Uso
1. Ejecuta la aplicación con: 
   ```bash
   python app.py

2. En el navegador ir a la ruta http://127.0.0.1:5000

## Estructura del proyecto

proyecto_especies/
│
├── .gitignore                 # Archivos y carpetas ignorados por Git
├── app.py                     # Archivo principal de la aplicación Flask
├── modelo_entrenado.h5        # Modelo entrenado de la red neuronal
├── modelo_entrenar.py         # Script para entrenar el modelo
├── modelo.py                  # Funciones relacionadas con el modelo de predicción
├── README.md                  # Documentación del proyecto
├── requirements.txt           # Dependencias del proyecto
├── scaler.save                # Escalador utilizado para normalizar los datos
│
├── data/                      # Archivos de datos
│   ├── especies_en_peligro.csv   # Datos históricos de población
│   ├── especies_en_peligro.xlsx  # Versión Excel de los datos históricos
│   ├── especies_extintas.csv     # Datos de especies extintas
│   ├── especies_extintas.xlsx    # Versión Excel de los datos extintos
│   ├── info_especies.csv         # Información detallada de las especies
│
├── static/                    # Archivos estáticos (CSS, JS, imágenes, etc.)
│   ├── data.json              # Datos en formato JSON
│   ├── css/                   # Archivos de estilos CSS
│   ├── img/                   # Imágenes utilizadas en la aplicación
│   ├── js/                    # Archivos JavaScript
│
├── templates/                 # Plantillas HTML para la interfaz de usuario
│   ├── ayudar.html            # Página de cómo ayudar
│   ├── blog.html              # Página de noticias y blogs
│   ├── casos_exito.html       # Página de casos de éxito
│   ├── estadisticas.html      # Página de estadísticas por especie
│   ├── galeria.html           # Página de galería de especies
│   ├── huella_carbono.html    # Página para calcular la huella de carbono
│   ├── huella_empresa.html    # Página para calcular la huella de carbono empresarial
│   ├── huella_persona.html    # Página para calcular la huella de carbono personal
│   ├── index.html             # Página principal
│   ├── layout.html            # Plantilla base para todas las páginas
│   ├── monitorizar.html       # Página de monitoreo de especies
│   ├── refugios.html          # Página de refugios y áreas protegidas
│

---

## Integrantes
- Rocio Ayala
- Gregory Barrientos
- Alejandro Campi
- Marcos Domínguez
- Ainhoa María
- Maria Mogollón
- Asier Villarubia