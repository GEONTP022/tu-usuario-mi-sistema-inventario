import streamlit as st
from supabase import create_client

# Conexión con los Secrets
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except:
    st.error("⚠️ Error: Faltan las llaves en Secrets de Streamlit.")
    st.stop()

st.set_page_config(page_title="Almacén Pro", layout="wide")

# --- INTERFAZ SUPERIOR ---
st.title("📦 Inventario de Repuestos")
busqueda = st.text_input("🔍 Buscar por modelo o tipo...", "").lower()

col_central, col_derecha = st.columns([3, 1])

# --- COLUMNA DERECHA: APARTADOS ---
with col_derecha:
    st.subheader("Apartados")
    if st.button("🔄 TODO", use_container_width=True): st.session_state.filtro = None
    if st.button("📱 PANTALLAS", use_container_width=True): st.session_state.filtro = "Pantallas"
    if st.button("🔋 BATERÍAS", use_container_width=True): st.session_state.filtro = "Baterías"
    if st.button("🔌 FLEX", use_container_width=True): st.session_state.filtro = "Flex"
    if st.button("💎 GLASES", use_container_width=True): st.session_state.filtro = "Glases"

# --- COLUMNA CENTRAL: PRODUCTOS ---
with col_central:
    filtro = st.session_state.get('filtro')
    st.write(f"Viendo: **{filtro if filtro else 'Todo'}**")
    
    # Consulta a Supabase
    query = supabase.table("productos").select("*")
    if filtro:
        query = query.eq("categoria", filtro)
    
    res = query.execute()
    
    if res.data:
        for p in res.data:
            if busqueda in p['nombre'].lower():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.markdown(f"### {p['nombre']}")
                    c2.metric("Stock", p['stock'])
                    
                    if c3.button(f"Salida (-1)", key=f"btn_{p['id']}"):
                        nuevo_stock = p['stock'] - 1
                        if nuevo_stock >= 0:
                            supabase.table("productos").update({"stock": nuevo_stock}).eq("id", p['id']).execute()
                            st.success(f"Salida de {p['nombre']}!")
                            st.rerun()
                        else:
                            st.error("Sin stock")
    else:
        st.info("No hay productos cargados aún.")
