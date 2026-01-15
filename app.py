import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="VillaFix | Gestión", page_icon="🔐", layout="wide")

# --- ESTADO DE SESIÓN ---
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
            try:
                res = supabase.table("usuarios").select("*").eq("usuario", u).eq("contrasena", p).execute()
                if res.data:
                    st.session_state.autenticado = True
                    st.session_state.rol = res.data[0]['rol']
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
            except:
                st.error("Error: Asegúrate de haber ejecutado el SQL en Supabase.")
    st.stop()

# --- DISEÑO UI ---
st.markdown("""
    <style>
    .stApp { background-color: #1e1e2f; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #11111b; min-width: 260px !important; }
    .sidebar-header { font-size: 13px; color: #6272a4; font-weight: bold; margin-top: 25px; text-transform: uppercase; letter-spacing: 1.5px; }
    
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #282a36 !important;
        border: 1px solid #44475a !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PANEL IZQUIERDO ---
with st.sidebar:
    st.markdown(f"<h1 style='color:#50fa7b; text-align:center;'>VillaFix</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>Usuario: <b>{st.session_state.user}</b> ({st.session_state.rol})</p>", unsafe_allow_html=True)
    if st.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
    st.write("---")
    
    st.markdown('<p class="sidebar-header">📦 Gestión de Almacén</p>', unsafe_allow_html=True)
    if st.button("🖼️ Inventario General", use_container_width=True): st.session_state.menu = "Stock"
    
    if st.session_state.rol == "Super":
        if st.button("➕ Ingreso de Mercancía", use_container_width=True): st.session_state.menu = "Carga"
        st.markdown('<p class="sidebar-header">🔄 Operaciones</p>', unsafe_allow_html=True)
        if st.button("📜 Historial Total", use_container_width=True): st.session_state.menu = "Log"
        if st.button("📊 Estadísticas", use_container_width=True): st.session_state.menu = "Stats"
        st.markdown('<p class="sidebar-header">⚙️ Configuración</p>', unsafe_allow_html=True)
        if st.button("👤 Gestionar Usuarios", use_container_width=True): st.session_state.menu = "Users"

# --- SECCIÓN: INVENTARIO ---
if st.session_state.menu == "Stock":
    st.markdown("<h1 style='color:#50fa7b;'>INVENTARIO GENERAL - VILLAFIX</h1>", unsafe_allow_html=True)
    col_a, col_b = st.columns([3, 1])
    with col_a: busqueda = st.text_input("", placeholder="🔍 Buscar repuesto...")
    with col_b: categoria = st.selectbox("Apartado", ["Todos", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])

    query = supabase.table("productos").select("*").order("nombre")
    if categoria != "Todos": query = query.eq("categoria", categoria)
    res = query.execute().data

    if res:
        cols = st.columns(4)
        for i, p in enumerate(res):
            if busqueda.lower() in p['nombre'].lower():
                with cols[i % 4]:
                    with st.container(border=True):
                        st.image(p.get('imagen_url') or "https://via.placeholder.com/150", use_container_width=True)
                        st.markdown(f"### {p['nombre']}")
                        color_stock = "#ff5555" if p['stock'] <= 3 else "#50fa7b"
                        c_s, c_p = st.columns(2)
                        c_s.markdown(f"Stock: <br><span style='color:{color_stock}; font-size:22px; font-weight:bold;'>{p['stock']}</span>", unsafe_allow_html=True)
                        c_p.markdown(f"Precio: <br><span style='font-size:22px; font-weight:bold;'>S/ {p['precio_venta']}</span>", unsafe_allow_html=True)
                        
                        if st.button(f"REGISTRAR SALIDA", key=f"btn_{p['id']}", use_container_width=True):
                            if p['stock'] > 0:
                                supabase.table("productos").update({"stock": p['stock'] - 1}).eq("id", p['id']).execute()
                                # AQUÍ GUARDAMOS EL USUARIO QUE HACE LA SALIDA
                                supabase.table("historial").insert({
                                    "producto_nombre": p['nombre'], 
                                    "cantidad": -1, 
                                    "usuario": st.session_state.user 
                                }).execute()
                                st.rerun()
    else:
        st.info("No hay productos cargados.")

# --- SECCIÓN: GESTIÓN DE USUARIOS ---
elif st.session_state.menu == "Users" and st.session_state.rol == "Super":
    st.header("👤 Registro de Usuarios")
    with st.form("new_u"):
        nu = st.text_input("Nombre de Usuario")
        np = st.text_input("Contraseña")
        nr = st.selectbox("Rol", ["Normal", "Super"])
        if st.form_submit_button("CREAR USUARIO"):
            if nu and np:
                supabase.table("usuarios").insert({"usuario":nu, "contrasena":np, "rol":nr}).execute()
                st.success(f"Usuario {nu} creado.")
            else:
                st.error("Completa todos los campos.")
