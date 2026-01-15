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
    st.markdown("<h1 style='text-align:center; color:#2488bc;'>VILLAFIX ACCESS</h1>", unsafe_allow_html=True)
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

# --- DISEÑO UI (BARRA AZUL, ICONOS BLANCOS, ALINEACIÓN IZQUIERDA) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; color: #1e1e2f; }
    
    [data-testid="stSidebar"] {
        background-color: #2488bc !important;
        color: white !important;
        padding: 0px !important;
    }

    /* Contenedor del Logo y Título */
    .sidebar-brand-container {
        padding: 20px 0px 5px 15px;
        text-align: left;
    }

    .sidebar-title {
        color: white; font-size: 20px; font-weight: bold;
        margin-top: 10px;
    }

    .sidebar-user {
        font-size: 13px; color: rgba(255,255,255,0.8);
        padding-left: 15px; margin-bottom: 20px;
    }

    .stSidebar .stButton>button {
        background-color: transparent; color: white; border: none;
        border-radius: 25px 0px 0px 25px; height: 45px;
        margin-left: 10px; width: calc(100% - 10px);
        text-align: left; font-size: 15px; transition: 0.3s;
        padding-left: 15px;
    }
    
    .stSidebar .stButton>button:hover, .stSidebar .stButton>button:focus {
        background-color: #ffffff !important;
        color: #2488bc !important;
        font-weight: bold;
    }

    .sidebar-header {
        font-size: 11px; color: rgba(255,255,255,0.6);
        font-weight: bold; margin: 25px 0px 5px 15px;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PANEL IZQUIERDO ---
with st.sidebar:
    # --- AQUÍ PUEDES PONER TU LOGO ---
    # Opción 1: Link de internet. Opción 2: Sube el archivo a GitHub y usa "tu_logo.png"
    url_tu_logo = "https://cdn-icons-png.flaticon.com/512/2991/2991148.png" # <--- CAMBIA ESTE LINK
    
    st.markdown('<div class="sidebar-brand-container">', unsafe_allow_html=True)
    st.image(url_tu_logo, width=60) # Ajusta el ancho según tu logo
    st.markdown('<div class="sidebar-title">VillaFix Admin</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="sidebar-user">👤 {st.session_state.user}</div>', unsafe_allow_html=True)
    
    # ... Resto del menú lateral igual ...
    st.markdown('<p class="sidebar-header">Gestión</p>', unsafe_allow_html=True)
    if st.button("⬜ Inicio / Stock", use_container_width=True): st.session_state.menu = "Stock"
    
    if st.session_state.rol == "Super":
        if st.button("➕ Nuevo Producto", use_container_width=True): st.session_state.menu = "Carga"
        st.markdown('<p class="sidebar-header">Reportes</p>', unsafe_allow_html=True)
        if st.button("📋 Historial", use_container_width=True): st.session_state.menu = "Log"
        if st.button("📊 Estadísticas", use_container_width=True): st.session_state.menu = "Stats"
        st.markdown('<p class="sidebar-header">Admin</p>', unsafe_allow_html=True)
        if st.button("👥 Usuarios", use_container_width=True): st.session_state.menu = "Users"
        if st.button("📞 Proveedores", use_container_width=True): st.session_state.menu = "Prov"

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# --- LÓGICA DE SECCIONES (STOCK, CARGA, LOG, STATS, USERS, PROV) ---
# (Mantener igual que el código anterior sin cambios)
opcion = st.session_state.menu

if opcion == "Stock":
    st.markdown("<h2 style='color:#2488bc;'>Inventario General</h2>", unsafe_allow_html=True)
    # ... código de inventario ...
    items = supabase.table("productos").select("*").order("nombre").execute().data
    if items:
        cols = st.columns(4)
        for i, p in enumerate(items):
            # (Busqueda y filtro de categoria...)
            with cols[i % 4]:
                with st.container(border=True):
                    st.image(p.get('imagen_url') or "https://via.placeholder.com/150", use_container_width=True)
                    st.markdown(f"**{p['nombre']}**")
                    cs, cp = st.columns(2)
                    cs.write(f"U: {p['stock']}")
                    cp.write(f"S/ {p['precio_venta']}")
                    if st.button("SALIDA", key=f"s_{p['id']}", use_container_width=True):
                        if p['stock'] > 0:
                            supabase.table("productos").update({"stock": p['stock']-1}).eq("id", p['id']).execute()
                            supabase.table("historial").insert({"producto_nombre":p['nombre'], "cantidad":-1, "usuario":st.session_state.user}).execute()
                            st.rerun()

elif opcion == "Carga":
    st.header("➕ Nuevo Producto")
    with st.form("form_carga"):
        n = st.text_input("Modelo / Repuesto *")
        c = st.selectbox("Categoría *", ["Pantallas", "Baterías", "Flex", "Glases", "Otros"])
        s = st.number_input("Stock inicial", min_value=1)
        p = st.number_input("Precio Venta (S/)", min_value=0.0)
        img = st.text_input("URL Imagen")
        if st.form_submit_button("GUARDAR EN VILLAFIX"):
            if n and c:
                supabase.table("productos").insert({"nombre":n, "categoria":c, "stock":s, "precio_venta":p, "imagen_url":img}).execute()
                st.success("Guardado.")

elif opcion == "Log":
    st.header("📜 Historial")
    logs = supabase.table("historial").select("*").order("fecha", desc=True).execute().data
    if logs:
        df = pd.DataFrame(logs)
        df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m %H:%M')
        st.dataframe(df[['fecha', 'producto_nombre', 'cantidad', 'usuario']], use_container_width=True, hide_index=True)

elif opcion == "Stats":
    st.header("📊 Estadísticas")
    p_data = supabase.table("productos").select("*").execute().data
    if p_data:
        df_p = pd.DataFrame(p_data)
        fig = px.pie(df_p, names='categoria', values='stock', hole=0.4, title="Stock por Categoría")
        st.plotly_chart(fig, use_container_width=True)

elif opcion == "Users":
    st.header("👥 Usuarios")
    with st.form("nu"):
        un, pw, rl = st.text_input("Usuario"), st.text_input("Clave"), st.selectbox("Rol", ["Normal", "Super"])
        if st.form_submit_button("CREAR"):
            supabase.table("usuarios").insert({"usuario":un, "contrasena":pw, "rol":rl}).execute()
            st.success("Usuario creado.")

elif opcion == "Prov":
    st.header("📞 Proveedores")
    provs = supabase.table("proveedores").select("*").execute().data
    if provs:
        for pr in provs:
            with st.container(border=True):
                st.write(f"**{pr['nombre_contacto']}**")
                st.link_button("WhatsApp", f"https://wa.me/{pr['whatsapp']}")
