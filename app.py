import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONEXIÓN A BASE DE DATOS ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VillaFix | Admin", page_icon="🛠️", layout="wide")

# --- LÓGICA DE SESIÓN (LOGIN) ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.rol = None
    st.session_state.user = None
    st.session_state.menu = "Stock"

# --- INTERFAZ DE ACCESO ---
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align:center; color:#2488bc;'>VILLAFIX ACCESS</h1>", unsafe_allow_html=True)
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
                    st.error("Credenciales incorrectas")
            except Exception as e:
                st.error(f"Error de conexión: {e}")
    st.stop()

# --- DISEÑO UI PREMIUM (SIDEBAR FIJO CON PERFIL) ---
st.markdown("""
    <style>
    /* Fondo principal y tipografía */
    .stApp { background-color: #f8f9fa; color: #1e1e2f; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* SIDEBAR FIJO Y OSCURO */
    [data-testid="stSidebar"] {
        background-color: #1a222b !important;
        color: white !important;
        min-width: 280px !important;
        border-right: 1px solid #2c3e50;
    }

    /* CONTENEDOR DE PERFIL (Basado en imagen image_6cc48a.png) */
    .profile-section {
        text-align: center;
        padding: 30px 10px;
        background: #1a222b;
    }
    .profile-pic {
        width: 110px;
        height: 110px;
        border-radius: 50%;
        border: 4px solid #f39c12; /* Borde naranja de la referencia */
        margin-bottom: 15px;
        object-fit: cover;
    }
    .profile-name {
        font-size: 18px;
        font-weight: bold;
        color: white;
        margin: 0;
    }
    .profile-status {
        font-size: 13px;
        color: #95a5a6;
        margin-bottom: 10px;
    }

    /* SEPARADOR AZUL DELGADO */
    .sidebar-divider {
        height: 1px;
        background-color: #3498db;
        margin: 5px 0 15px 0;
        width: 100%;
    }

    /* BOTONES DE MENÚ ALINEADOS A LA IZQUIERDA */
    .stSidebar .stButton>button {
        background-color: transparent;
        color: #bdc3c7;
        border: none;
        border-radius: 0;
        height: 50px;
        text-align: left;
        font-size: 15px;
        width: 100%;
        padding-left: 20px;
        transition: all 0.2s ease;
        border-left: 0px solid #3498db;
    }
    
    /* Hover y Selección activa */
    .stSidebar .stButton>button:hover, .stSidebar .stButton>button:active {
        background-color: #2c3e50 !important;
        color: white !important;
        border-left: 5px solid #3498db !important;
    }

    /* Ocultar elementos innecesarios */
    [data-testid="stSidebarNav"] {display: none;}
    
    /* Ajuste de tarjetas de productos */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border-radius: 12px !important;
        border: 1px solid #e1e4e8 !important;
        padding: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PANEL IZQUIERDO (SIDEBAR) ---
with st.sidebar:
    # SECCIÓN DE PERFIL
    st.markdown(f"""
        <div class="profile-section">
            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" class="profile-pic">
            <p class="profile-name">{st.session_state.user.capitalize()}</p>
            <p class="profile-status">Administrador</p>
        </div>
        <div class="sidebar-divider"></div>
    """, unsafe_allow_html=True)
    
    # NAVEGACIÓN (Iconos monocromáticos blancos)
    if st.button("⬜ Dashboard / Stock", use_container_width=True): st.session_state.menu = "Stock"
    
    if st.session_state.rol == "Super":
        if st.button("⬜ Nuevo Producto", use_container_width=True): st.session_state.menu = "Carga"
        if st.button("⬜ Historial", use_container_width=True): st.session_state.menu = "Log"
        if st.button("⬜ Estadísticas", use_container_width=True): st.session_state.menu = "Stats"
        if st.button("⬜ Usuarios", use_container_width=True): st.session_state.menu = "Users"
        if st.button("⬜ Proveedores", use_container_width=True): st.session_state.menu = "Prov"

    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# --- ÁREA CENTRAL ---
opcion = st.session_state.menu

if opcion == "Stock":
    st.markdown("<h2 style='color:#1a222b;'>Inventario General</h2>", unsafe_allow_html=True)
    col_a, col_b = st.columns([3, 1])
    with col_a: busqueda = st.text_input("", placeholder="🔍 Buscar repuesto...")
    with col_b: categoria = st.selectbox("Categoría", ["Todos", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])

    items = supabase.table("productos").select("*").order("nombre").execute().data
    if items:
        cols = st.columns(4)
        for i, p in enumerate(items):
            if (categoria == "Todos" or p['categoria'] == categoria) and (busqueda.lower() in p['nombre'].lower()):
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
                                supabase.table("historial").insert({
                                    "producto_nombre": p['nombre'], 
                                    "cantidad": -1, 
                                    "usuario": st.session_state.user
                                }).execute()
                                st.rerun()

elif opcion == "Carga":
    st.header("➕ Nuevo Producto")
    with st.form("form_carga"):
        n = st.text_input("Modelo / Repuesto *")
        c = st.selectbox("Categoría *", ["Pantallas", "Baterías", "Flex", "Glases", "Otros"])
        s = st.number_input("Stock inicial", min_value=1)
        p = st.number_input("Precio Venta (S/)", min_value=0.0)
        img = st.text_input("URL Imagen")
        if st.form_submit_button("GUARDAR"):
            if n and c:
                supabase.table("productos").insert({"nombre":n, "categoria":c, "stock":s, "precio_venta":p, "imagen_url":img}).execute()
                st.success("Guardado correctamente.")

elif opcion == "Log":
    st.header("📜 Historial de Movimientos")
    logs = supabase.table("historial").select("*").order("fecha", desc=True).execute().data
    if logs:
        df = pd.DataFrame(logs)
        df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m/%Y %H:%M')
        st.dataframe(df[['fecha', 'producto_nombre', 'cantidad', 'usuario']], use_container_width=True, hide_index=True)

elif opcion == "Stats":
    st.header("📊 Estadísticas")
    p_data = supabase.table("productos").select("*").execute().data
    if p_data:
        df_p = pd.DataFrame(p_data)
        fig = px.pie(df_p, names='categoria', values='stock', hole=0.4, title="Distribución de Stock")
        st.plotly_chart(fig, use_container_width=True)

elif opcion == "Users":
    st.header("👥 Gestión de Usuarios")
    with st.form("nu"):
        un = st.text_input("Usuario")
        pw = st.text_input("Clave")
        rl = st.selectbox("Rol", ["Normal", "Super"])
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
