import streamlit as st
from supabase import create_client

# Conexión con los Secrets de Streamlit
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Almacén Pro", layout="wide")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    .stTextInput>div>div>input { font-size: 20px; }
    </style>
    """, unsafe_allow_config=True)

# --- INTERFAZ SUPERIOR ---
st.title("📦 Sistema de Inventario de Repuestos")
busqueda = st.text_input("🔍 Buscar por modelo o tipo de repuesto...", "").lower()

col_central, col_derecha = st.columns([3, 1])

# --- COLUMNA DERECHA: CATEGORÍAS ---
with col_derecha:
    st.subheader("Apartados")
    if st.button("🔄 MOSTRAR TODO"): st.session_state.filtro = None
    if st.button("📱 PANTALLAS"): st.session_state.filtro = "Pantallas"
    if st.button("🔋 BATERÍAS"): st.session_state.filtro = "Baterías"
    if st.button("🔌 FLEX"): st.session_state.filtro = "Flex"
    if st.button("💎 GLASES"): st.session_state.filtro = "Glases"

# --- COLUMNA CENTRAL: PRODUCTOS ---
with col_central:
    filtro = st.session_state.get('filtro')
    st.write(f"Filtrando por: **{filtro if filtro else 'Todo'}**")
    
    # Consulta a Supabase
    query = supabase.table("productos").select("*")
    if filtro:
        query = query.eq("categoria", filtro)
    
    res = query.execute()
    
    if res.data:
        for p in res.data:
            # Filtro de búsqueda visual
            if busqueda in p['nombre'].lower():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.markdown(f"### {p['nombre']}")
                    c2.metric("Stock Actual", p['stock'])
                    
                    # Botón de Salida con lógica simple
                    if c3.button(f"Registrar Salida", key=f"btn_{p['id']}"):
                        nuevo_stock = p['stock'] - 1
                        if nuevo_stock >= 0:
                            supabase.table("productos").update({"stock": nuevo_stock}).eq("id", p['id']).execute()
                            st.success(f"Salida de {p['nombre']} registrada.")
                            st.rerun()
                        else:
                            st.error("No hay stock suficiente.")
    else:
        st.info("No hay productos en esta categoría. Agrega algunos en Supabase.")
