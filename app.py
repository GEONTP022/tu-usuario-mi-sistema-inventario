import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="VillaFix | Acceso", page_icon="🔐", layout="wide")

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
                st.error("Error técnico: Verifica si creaste la tabla 'usuarios' en Supabase.")
    st.stop()

# --- DISEÑO UI ---
st.markdown("""
    <style>
    .stApp { background-color: #1e1e2f; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #11111b; min-width: 260px !important; }
    .sidebar-header { font-size: 12px; color: #6272a4; font-weight: bold; margin-top: 20px; text-transform: uppercase; letter-spacing: 1px; }
    </style>
    """, unsafe_allow_html=True)

# --- MENÚ LATERAL ORGANIZADO ---
with st.sidebar:
    st.markdown(f"<h1 style='color:#50fa7b; text-align:center;'>VillaFix</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>Bienvenido, <b>{st.session_state.user}</b></p>", unsafe_allow_html=True)
    if st.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
    st.write("---")
    
    # CATEGORÍA 1: ALMACÉN
    st.markdown('<p class="sidebar-header">📦 Gestión de Almacén</p>', unsafe_allow_html=True)
    if st.button("🖼️ Inventario General", use_container_width=True): st.session_state.menu = "Stock"
    
    # OPCIONES SOLO PARA SUPER USUARIO
    if st.session_state.rol == "Super":
        if st.button("➕ Nuevo Repuesto", use_container_width=True): st.session_state.menu = "Carga"
        
        st.markdown('<p class="sidebar-header">📈 Análisis y Control</p>', unsafe_allow_html=True)
        if st.button("📊 Estadísticas", use_container_width=True): st.session_state.menu = "Stats"
        if st.button("📜 Historial Total", use_container_width=True): st.session_state.menu = "Log"
        
        st.markdown('<p class="sidebar-header">⚙️ Configuración</p>', unsafe_allow_html=True)
        if st.button("👤 Crear Usuarios", use_container_width=True): st.session_state.menu = "Users"
        if st.button("📞 Proveedores", use_container_width=True): st.session_state.menu = "Prov"

# --- SECCIONES ---
if st.session_state.menu == "Stock":
    st.markdown("<h1 style='color:#50fa7b;'>INVENTARIO GENERAL - VILLAFIX</h1>", unsafe_allow_html=True)
    # ... aquí sigue tu código de filtros y tarjetas de productos ...
    # IMPORTANTE: Al registrar salida, ahora guardamos el usuario:
    # supabase.table("historial").insert({"producto_nombre": p['nombre'], "cantidad": -1, "usuario": st.session_state.user}).execute()

elif st.session_state.menu == "Users" and st.session_state.rol == "Super":
    st.header("👤 Registro de Colaboradores")
    with st.form("new_u"):
        nu = st.text_input("Nombre de Usuario")
        np = st.text_input("Contraseña")
        nr = st.selectbox("Rol", ["Normal", "Super"])
        if st.form_submit_button("CREAR ACCESO"):
            if nu and np:
                supabase.table("usuarios").insert({"usuario":nu, "contrasena":np, "rol":nr}).execute()
                st.success(f"Usuario {nu} registrado con éxito.")
