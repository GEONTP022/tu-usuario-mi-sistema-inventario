import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="VillaFix | Sistema", page_icon="🛠️", layout="wide")

# --- LÓGICA DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.rol = None
    st.session_state.user = None
    st.session_state.menu = "Stock"

# --- LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align:center; color:#50fa7b;'>VILLAFIX ACCESS</h1>", unsafe_allow_html=True)
    with st.container(border=True):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("INGRESAR AL SISTEMA", use_container_width=True):
            res = supabase.table("usuarios").select("*").eq("usuario", u).eq("contrasena", p).execute()
            if res.data:
                st.session_state.autenticado = True
                st.session_state.rol = res.data[0]['rol']
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
    st.stop()

# --- DISEÑO UI REFINADO (MENÚ A LA IZQUIERDA + ICONOS BLANCOS) ---
st.markdown("""
    <style>
    /* Fondo principal */
    .stApp { background-color: #f8f9fa; color: #1e1e2f; }
    
    /* BARRA LATERAL */
    [data-testid="stSidebar"] {
        background-color: #2488bc !important;
        color: white !important;
        padding: 0px !important;
    }

    /* Título Pegado a la Izquierda */
    .sidebar-title {
        color: white;
        font-size: 20px;
        font-weight: bold;
        padding: 20px 0px 10px 15px;
        text-align: left;
    }

    /* Subtítulo pegado a la izquierda */
    .sidebar-user {
        font-size: 13px;
        color: rgba(255,255,255,0.8);
        padding-left: 15px;
        margin-bottom: 20px;
    }

    /* BOTONES DE NAVEGACIÓN ESTILO PÍLDORA */
    /* Quitamos el margen lateral para que peguen más a la izquierda */
    .stSidebar .stButton>button {
        background-color: transparent;
        color: white;
        border: none;
        border-radius: 25px 0px 0px 25px; /* Efecto pestaña */
        height: 45px;
        margin-left: 10px; /* Espacio mínimo para que se vea el redondeado */
        width: calc(100% - 10px);
        text-align: left;
        font-size: 15px;
        transition: 0.3s;
        display: flex;
        align-items: center;
        padding-left: 15px;
    }
    
    /* Efecto Activo (Blanco) */
    .stSidebar .stButton>button:hover, .stSidebar .stButton>button:focus {
        background-color: #ffffff !important;
        color: #2488bc !important;
        font-weight: bold;
    }

    /* Encabezados de categorías */
    .sidebar-header {
        font-size: 11px;
        color: rgba(255,255,255,0.6);
        font-weight: bold;
        margin: 25px 0px 5px 15px;
        text-transform: uppercase;
    }

    /* Ajustar las imágenes de las tarjetas */
    .stImage > img {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PANEL IZQUIERDO RE-DISEÑADO ---
with st.sidebar:
    st.markdown('<div class="sidebar-title">🏦 VillaFix Admin</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-user">👤 {st.session_state.user}</div>', unsafe_allow_html=True)
    
    # SECCIÓN 1: ALMACÉN
    st.markdown('<p class="sidebar-header">Gestión</p>', unsafe_allow_html=True)
    # Usamos iconos de Streamlit (Material Icons) que son de un solo color
    if st.button("🏠 Inicio / Stock", use_container_width=True): st.session_state.menu = "Stock"
    
    if st.session_state.rol == "Super":
        if st.button("📥 Nuevo Producto", use_container_width=True): st.session_state.menu = "Carga"
        
        # SECCIÓN 2: OPERACIONES
        st.markdown('<p class="sidebar-header">Reportes</p>', unsafe_allow_html=True)
        if st.button("📋 Historial", use_container_width=True): st.session_state.menu = "Log"
        if st.button("📊 Estadísticas", use_container_width=True): st.session_state.menu = "Stats"
        
        # SECCIÓN 3: CONFIG
        st.markdown('<p class="sidebar-header">Admin</p>', unsafe_allow_html=True)
        if st.button("👥 Usuarios", use_container_width=True): st.session_state.menu = "Users"
        if st.button("📞 Proveedores", use_container_width=True): st.session_state.menu = "Prov"

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# --- ÁREA CENTRAL ---
opcion = st.session_state.menu

if opcion == "Stock":
    st.markdown("<h2 style='color:#2488bc; font-weight:bold;'>Inventario General</h2>", unsafe_allow_html=True)
    col_a, col_b = st.columns([3, 1])
    with col_a: busqueda = st.text_input("", placeholder="🔍 Buscar modelo o repuesto...")
    with col_b: categoria = st.selectbox("Categoría", ["Todos", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])

    items = supabase.table("productos").select("*").order("nombre").execute().data
    if items:
        cols = st.columns(4)
        for i, p in enumerate(items):
            if (categoria == "Todos" or p['categoria'] == categoria) and (busqueda.lower() in p['nombre'].lower()):
                with cols[i % 4]:
                    with st.container(border=True):
                        st.image(p.get('imagen_url') or "https://via.placeholder.com/150", use_container_width=True)
                        st.markdown(f"<p style='font-weight:bold; margin-bottom:0;'>{p['nombre']}</p>", unsafe_allow_html=True)
                        cs, cp = st.columns(2)
                        cs.markdown(f"<small>Stock: {p['stock']}</small>", unsafe_allow_html=True)
                        cp.markdown(f"<small>S/ {p['precio_venta']}</small>", unsafe_allow_html=True)
                        if st.button("SALIDA (-1)", key=f"s_{p['id']}", use_container_width=True):
                            if p['stock'] > 0:
                                supabase.table("productos").update({"stock": p['stock']-1}).eq("id", p['id']).execute()
                                supabase.table("historial").insert({"producto_nombre":p['nombre'], "cantidad":-1, "usuario":st.session_state.user}).execute()
                                st.rerun()

elif opcion == "Log":
    st.markdown("<h2 style='color:#2488bc;'>Historial</h2>", unsafe_allow_html=True)
    logs = supabase.table("historial").select("*").order("fecha", desc=True).execute().data
    if logs:
        df = pd.DataFrame(logs)
        df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m %H:%M')
        st.dataframe(df[['fecha', 'producto_nombre', 'cantidad', 'usuario']], use_container_width=True, hide_index=True)

# (Se mantienen las demás secciones de Carga, Stats, etc. con el mismo código lógico anterior)
