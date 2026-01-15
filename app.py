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

# --- DISEÑO UI MEJORADO (BARRA AZUL) ---
st.markdown("""
    <style>
    /* Fondo principal */
    .stApp { background-color: #f0f2f6; color: #1e1e2f; }
    
    /* BARRA LATERAL ESTILO "INFO VENTAS" */
    [data-testid="stSidebar"] {
        background-color: #2488bc !important; /* Azul de la imagen */
        color: white !important;
        min-width: 280px !important;
    }
    
    /* Titulo de la barra lateral */
    .sidebar-title {
        color: white;
        font-size: 24px;
        font-weight: bold;
        padding: 20px 0px;
        text-align: center;
        border-bottom: 1px solid rgba(255,255,255,0.2);
        margin-bottom: 20px;
    }

    /* BOTONES DE NAVEGACIÓN (TIPO PÍLDORA) */
    .stSidebar .stButton>button {
        background-color: transparent;
        color: white;
        border: none;
        border-radius: 30px 0px 0px 30px; /* Redondeado solo a la izquierda como la foto */
        height: 50px;
        margin-left: 20px;
        width: 100%;
        text-align: left;
        font-size: 16px;
        transition: 0.3s;
    }
    
    /* Efecto cuando el botón está activo o se pasa el mouse */
    .stSidebar .stButton>button:hover, .stSidebar .stButton>button:focus {
        background-color: #ffffff !important;
        color: #2488bc !important;
        font-weight: bold;
        box-shadow: -5px 5px 15px rgba(0,0,0,0.1);
    }

    /* Encabezados de categorías en blanco */
    .sidebar-header {
        font-size: 11px;
        color: rgba(255,255,255,0.7);
        font-weight: bold;
        margin: 20px 0px 5px 30px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Tarjetas de inventario blancas para resaltar sobre el fondo gris */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border: 1px solid #e1e4e8 !important;
        border-radius: 15px !important;
        color: #1e1e2f !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PANEL IZQUIERDO RE-DISEÑADO ---
with st.sidebar:
    st.markdown('<div class="sidebar-title">🏦 Info VillaFix</div>', unsafe_allow_html=True)
    st.write(f"Conectado: **{st.session_state.user}**")
    
    # SECCIÓN 1: ALMACÉN
    st.markdown('<p class="sidebar-header">📦 Gestión</p>', unsafe_allow_html=True)
    if st.button("🏠 Inicio / Stock", use_container_width=True): st.session_state.menu = "Stock"
    
    if st.session_state.rol == "Super":
        if st.button("📥 Nuevo Producto", use_container_width=True): st.session_state.menu = "Carga"
        
        # SECCIÓN 2: OPERACIONES
        st.markdown('<p class="sidebar-header">🔄 Reportes</p>', unsafe_allow_html=True)
        if st.button("📋 Historial", use_container_width=True): st.session_state.menu = "Log"
        if st.button("📊 Estadísticas", use_container_width=True): st.session_state.menu = "Stats"
        
        # SECCIÓN 3: CONFIG
        st.markdown('<p class="sidebar-header">⚙️ Admin</p>', unsafe_allow_html=True)
        if st.button("👤 Usuarios", use_container_width=True): st.session_state.menu = "Users"
        if st.button("📞 Proveedores", use_container_width=True): st.session_state.menu = "Prov"

    st.write("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# --- ÁREA CENTRAL (Mantiene toda tu lógica anterior) ---
opcion = st.session_state.menu

if opcion == "Stock":
    st.markdown("<h1 style='color:#2488bc;'>INVENTARIO GENERAL</h1>", unsafe_allow_html=True)
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
                        st.markdown(f"<h4 style='color:#1e293b;'>{p['nombre']}</h4>", unsafe_allow_html=True)
                        cs, cp = st.columns(2)
                        cs.write(f"Stock: **{p['stock']}**")
                        cp.write(f"**S/ {p['precio_venta']}**")
                        if st.button("REGISTRAR SALIDA", key=f"s_{p['id']}", use_container_width=True):
                            if p['stock'] > 0:
                                supabase.table("productos").update({"stock": p['stock']-1}).eq("id", p['id']).execute()
                                supabase.table("historial").insert({"producto_nombre":p['nombre'], "cantidad":-1, "usuario":st.session_state.user}).execute()
                                st.rerun()

elif opcion == "Carga":
    st.header("📥 Ingreso de Mercancía")
    with st.form("form_carga"):
        n = st.text_input("Modelo / Repuesto *")
        c = st.selectbox("Categoría *", ["Pantallas", "Baterías", "Flex", "Glases", "Otros"])
        s = st.number_input("Stock", min_value=1)
        p = st.number_input("Precio (S/)", min_value=0.0)
        img = st.text_input("URL Imagen")
        if st.form_submit_button("GUARDAR"):
            if n and c:
                supabase.table("productos").insert({"nombre":n, "categoria":c, "stock":s, "precio_venta":p, "imagen_url":img}).execute()
                st.success("Guardado.")

elif opcion == "Log":
    st.header("📋 Historial")
    logs = supabase.table("historial").select("*").order("fecha", desc=True).execute().data
    if logs:
        df = pd.DataFrame(logs)
        st.dataframe(df[['fecha', 'producto_nombre', 'cantidad', 'usuario']], use_container_width=True)

elif opcion == "Stats":
    st.header("📊 Estadísticas")
    p_data = supabase.table("productos").select("*").execute().data
    if p_data:
        df_p = pd.DataFrame(p_data)
        fig = px.pie(df_p, names='categoria', values='stock', hole=0.4, title="Stock por Categoría")
        st.plotly_chart(fig, use_container_width=True)

elif opcion == "Users":
    st.header("👤 Usuarios")
    with st.form("nu"):
        un, pw, rl = st.text_input("Usuario"), st.text_input("Clave"), st.selectbox("Rol", ["Normal", "Super"])
        if st.form_submit_button("CREAR"):
            supabase.table("usuarios").insert({"usuario":un, "contrasena":pw, "rol":rl}).execute()
            st.success("Creado.")
