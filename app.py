import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="VillaFix | Acceso", page_icon="🔐", layout="wide")

# --- LÓGICA DE LOGIN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.rol = None
    st.session_state.user = None

def login():
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

# --- SI NO ESTÁ LOGUEADO, MOSTRAR LOGIN ---
if not st.session_state.autenticado:
    login()
    st.stop()

# --- SI ESTÁ LOGUEADO, MOSTRAR EL SISTEMA ---
# (Diseño UI igual al anterior...)
st.markdown("""
    <style>
    .stApp { background-color: #1e1e2f; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #11111b; min-width: 250px !important; }
    .sidebar-header { font-size: 13px; color: #6272a4; font-weight: bold; margin-top: 25px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"<h1 style='color:#50fa7b; text-align:center;'>VillaFix</h1>", unsafe_allow_html=True)
    st.write(f"👤 Usuario: **{st.session_state.user}**")
    st.caption(f"Acceso: {st.session_state.rol}")
    if st.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
    st.write("---")
    
    # --- FILTRO DE MENÚ POR ROL ---
    st.markdown('<p class="sidebar-header">📦 Almacén</p>', unsafe_allow_html=True)
    if st.button("🖼️ Ver Inventario", use_container_width=True): st.session_state.menu = "Stock"
    
    # Solo el Súper Usuario ve estas opciones
    if st.session_state.rol == "Super":
        if st.button("➕ Ingreso de Mercancía", use_container_width=True): st.session_state.menu = "Carga"
        
        st.markdown('<p class="sidebar-header">🔄 Operaciones</p>', unsafe_allow_html=True)
        if st.button("📜 Historial de Salidas", use_container_width=True): st.session_state.menu = "Log"
        if st.button("📊 Estadísticas de Uso", use_container_width=True): st.session_state.menu = "Stats"
        
        st.markdown('<p class="sidebar-header">👥 Directorio</p>', unsafe_allow_html=True)
        if st.button("📞 Proveedores", use_container_width=True): st.session_state.menu = "Prov"
        if st.button("👤 Crear Usuarios", use_container_width=True): st.session_state.menu = "Users"

# --- LÓGICA DE LAS SECCIONES ---
# Aquí pegas el resto de tu código de Stock, Carga, Log, Stats, etc.

if st.session_state.menu == "Users" and st.session_state.rol == "Super":
    st.header("👤 Gestión de Usuarios del Sistema")
    with st.form("new_user"):
        new_u = st.text_input("Nombre de Usuario")
        new_p = st.text_input("Contraseña")
        new_r = st.selectbox("Rol", ["Normal", "Super"])
        if st.form_submit_button("REGISTRAR NUEVO USUARIO"):
            supabase.table("usuarios").insert({"usuario": new_u, "contrasena": new_p, "rol": new_r}).execute()
            st.success(f"Usuario {new_u} creado correctamente.")
