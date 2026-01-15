import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="VillaFix | Gestión Profesional", page_icon="🛠️", layout="wide")

# --- DISEÑO UI REORGANIZADO ---
st.markdown("""
    <style>
    .stApp { background-color: #1e1e2f; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #11111b; min-width: 250px !important; }
    
    /* Estilo de los encabezados del menú lateral */
    .sidebar-header {
        font-size: 12px;
        color: #6272a4;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Tarjetas de Producto Estilo Moderno */
    .product-card {
        background-color: #282a36;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid #44475a;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PANEL IZQUIERDO: CLASIFICACIÓN LÓGICA ---
with st.sidebar:
    st.markdown("<h1 style='color:#50fa7b;'>VillaFix</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # --- GRUPO 1: ALMACÉN ---
    st.markdown('<p class="sidebar-header">📦 Gestión de Almacén</p>', unsafe_allow_html=True)
    if st.button("🖼️ Ver Inventario", use_container_width=True): st.session_state.menu = "Stock"
    if st.button("➕ Ingreso de Mercancía", use_container_width=True): st.session_state.menu = "Carga"
    
    # --- GRUPO 2: MOVIMIENTOS ---
    st.markdown('<p class="sidebar-header">🔄 Operaciones</p>', unsafe_allow_html=True)
    if st.button("📜 Historial de Salidas", use_container_width=True): st.session_state.menu = "Log"
    if st.button("📊 Estadísticas de Uso", use_container_width=True): st.session_state.menu = "Stats"
    
    # --- GRUPO 3: CONTACTOS ---
    st.markdown('<p class="sidebar-header">👥 Directorio</p>', unsafe_allow_html=True)
    if st.button("📞 Proveedores", use_container_width=True): st.session_state.menu = "Prov"

# --- ÁREA CENTRAL: LÓGICA DE NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Stock"
opcion = st.session_state.menu

if opcion == "Stock":
    st.header("🖼️ Inventario Visual")
    
    # Buscador y Filtros
    col_a, col_b = st.columns([3, 1])
    with col_a: busqueda = st.text_input("Buscador...", placeholder="Modelo de celular o repuesto")
    with col_b: categoria = st.selectbox("Apartado", ["Todos", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])

    # Carga de tarjetas
    query = supabase.table("productos").select("*").order("nombre")
    if categoria != "Todos": query = query.eq("categoria", categoria)
    items = query.execute().data

    if items:
        cols = st.columns(4)
        for i, p in enumerate(items):
            if busqueda.lower() in p['nombre'].lower():
                with cols[i % 4]:
                    with st.container(border=True):
                        st.image(p.get('imagen_url') or "https://via.placeholder.com/150", use_container_width=True)
                        st.markdown(f"**{p['nombre']}**")
                        color = "#ff5555" if p['stock'] <= 3 else "#50fa7b"
                        st.markdown(f"Unidades: <span style='color:{color}; font-weight:bold;'>{p['stock']}</span>", unsafe_allow_html=True)
                        st.write(f"S/ {p['precio_venta']}")
                        if st.button("REGISTRAR SALIDA", key=f"s_{p['id']}", use_container_width=True):
                            if p['stock'] > 0:
                                supabase.table("productos").update({"stock": p['stock']-1}).eq("id", p['id']).execute()
                                supabase.table("historial").insert({"producto_nombre":p['nombre'], "cantidad":-1}).execute()
                                st.rerun()

elif opcion == "Carga":
    st.header("➕ Agregar al Sistema")
    # Formulario para subir nuevos productos con imagen

elif opcion == "Stats":
    st.header("📊 Estadísticas VillaFix")
    # Gráficos de qué repuesto sale más
