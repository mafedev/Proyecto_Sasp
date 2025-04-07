import streamlit as st

def mostrar():
    st.title("🏢 Empresas y Conservación")

    if st.button("🏠 Volver al inicio"):
        st.session_state["pagina_actual"] = "Inicio"

    st.markdown("""
    Las empresas tienen un papel clave en la conservación del medio ambiente y la biodiversidad.

    ### ¿Cómo pueden ayudar?
    - 🌱 Reduciendo su huella ecológica
    - 💸 Invirtiendo en proyectos de restauración de hábitats
    - 🤝 Colaborando con ONGs ambientales
    - 📢 Educando a sus empleados y consumidores

    ### Ejemplos de iniciativas empresariales:
    - Tesla: uso de energía renovable
    - Patagonia: compromiso con el medio ambiente
    - Google: proyectos de sostenibilidad y datos para conservación

    Próximamente: integraráremos un sistema para que las empresas puedan registrarse y ver su impacto ambiental.
    """)