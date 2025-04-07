import streamlit as st
from paginas import inicio, monitorizar, buscar_especie, empresas

st.set_page_config(layout="wide")

# ----------------------- Estado inicial -----------------------
if "pagina_actual" not in st.session_state:
    st.session_state["pagina_actual"] = "Inicio"

# ----------------------- Función para navegar -----------------------
def ir_a(pagina):
    st.session_state["pagina_actual"] = pagina

# ----------------------- Sidebar y botón global -----------------------
st.sidebar.markdown("---")
if st.sidebar.button("🏠 Volver al inicio"):
    ir_a("Inicio")

if st.session_state["pagina_actual"] != "Inicio":
    if st.button("🏠 Volver al inicio", key="volver_inicio"):
        pagina_actual = "Inicio"

# ----------------------- Cargar página correspondiente -----------------------
paginas = {
    "Inicio": inicio.mostrar,
    "Monitorizar": monitorizar.mostrar,
    "Buscar": buscar_especie.mostrar,
    "Empresas": empresas.mostrar
}

paginas[st.session_state["pagina_actual"]](ir_a)  # Pasamos la función de navegación a cada página