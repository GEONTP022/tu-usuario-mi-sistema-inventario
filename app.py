import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Inventario Repuestos", layout="wide")

# Título y Buscador Superior
st.title("📱 Mi Almacén de Repuestos")
st.text_input("🔍 Buscar repuesto (ej: iPhone 12, Batería...)", key="buscador")

# Estructura de columnas: Centro (Productos) y Derecha (Apartados)
col_central, col_derecha = st.columns([3, 1])

with col_derecha:
    st.markdown("### Apartados")
    # Botones que pediste a la derecha
    if st.button("📱 PANTALLAS", use_container_width=True):
        st.session_state.filtro = "Pantallas"
    if st.button("🔋 BATERÍAS", use_container_width=True):
        st.session_state.filtro = "Baterías"
    if st.button("🔌 FLEX", use_container_width=True):
        st.session_state.filtro = "Flex"
    if st.button("💎 GLASES", use_container_width=True):
        st.session_state.filtro = "Glases"

with col_central:
    filtro_actual = st.session_state.get('filtro', 'Todos')
    st.subheader(f"Viendo: {filtro_actual}")
    st.info("Aquí aparecerán tus repuestos una vez conectemos la base de datos.")
