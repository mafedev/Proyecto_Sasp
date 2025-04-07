import streamlit as st

# Función que muestra la página de inicio
# Esta función se llama desde el archivo app.py para mostrar la página de inicio
def mostrar(ir_a):
    st.title("🌱 Bienvenido al Observatorio Global de Especies en Peligro")
    st.markdown("""
    Este dashboard utiliza datos abiertos y algoritmos de Inteligencia Artificial para:
    - 📊 Monitorizar poblaciones de especies en riesgo.
    - 🔍 Explorar especies mediante sus registros geográficos.
    - 💼 Conectar con iniciativas de conservación y empresas comprometidas.
    """)

    col1, col2, col3 = st.columns(3) # Crea tres columnas para los botones

    # Botones para navegar a diferentes páginas
    with col1:
        if st.button("🐾 Monitorizar especies en peligro"):
            ir_a("Monitorizar")
    with col2:
        if st.button("🔬 Buscar especie"):
            ir_a("Buscar")
    with col3:
        if st.button("🏢 Empresas"):
            ir_a("Empresas")
