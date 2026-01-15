import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONEXIÓN A BASE DE DATOS ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VillaFix | Sistema Integral", page_icon="🛠️", layout="wide")

# --- LÓGICA DE SESIÓN (LOGIN) ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.rol = None
    st.session_state.user = None
    st.session_state.menu = "Stock"

# --- INTERFAZ DE ACCESO ---
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
                    st.error("Credenciales incorrectas")
            except Exception as e:
                st.error(f"Error de conexión: {e}")
    st.stop()

# --- DISEÑO UI (CSS CUSTOM) ---
st.markdown("""
    <style>
    .stApp { background-color: #1e1e2f; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #11111b; min-width: 250px !important; }
    .sidebar-header { font-size: 13px; color: #6272a4; font-weight: bold; margin-top: 25px; text-transform: uppercase; letter-spacing: 1.5px; }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #282a36 !important;
        border: 1px solid #44475a !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PANEL IZQUIERDO (MENÚ CLASIFICADO) ---
with st.sidebar:
    st.markdown(f"<h1 style='color:#50fa7b; text-align:center;'>VillaFix</h1>", unsafe_allow_html=True)
    st.write(f"👤 **{st.session_state.user}** ({st.session_state.rol})")
    if st.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
    st.write("---")
    
    # SECCIÓN 1: ALMACÉN
    st.markdown('<p class="sidebar-header">📦 Gestión de Almacén</p>', unsafe_allow_html=True)
    if st.button("🖼️ Inventario General", use_container_width=True): st.session_state.menu = "Stock"
    
    # SOLO SUPER USUARIO VE ESTO
    if st.session_state.rol == "Super":
        if st.button("➕ Ingreso de Mercancía", use_container_width=True): st.session_state.menu = "Carga"
        
        st.markdown('<p class="sidebar-header">🔄 Operaciones</p>', unsafe_allow_html=True)
        if st.button("📜 Historial de Movimientos", use_container_width=True): st.session_state.menu = "Log"
        if st.button("📊 Estadísticas de Uso", use_container_width=True): st.session_state.menu = "Stats"
        
        st.markdown('<p class="sidebar-header">⚙️ Configuración</p>', unsafe_allow_html=True)
        if st.button("👤 Gestionar Usuarios", use_container_width=True): st.session_state.menu = "Users"
        if st.button("📞 Proveedores", use_container_width=True): st.session_state.menu = "Prov"

# --- NAVEGACIÓN DE SECCIONES ---
opcion = st.session_state.menu

# 1. INVENTARIO (ALMACÉN)
if opcion == "Stock":
    st.markdown("<h1 style='color:#50fa7b;'>INVENTARIO GENERAL - VILLAFIX</h1>", unsafe_allow_html=True)
    col_a, col_b = st.columns([3, 1])
    with col_a: busqueda = st.text_input("", placeholder="🔍 Buscar repuesto...")
    with col_b: categoria = st.selectbox("Apartado", ["Todos", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])

    items = supabase.table("productos").select("*").order("nombre").execute().data
    if items:
        cols = st.columns(4)
        for i, p in enumerate(items):
            if (categoria == "Todos" or p['categoria'] == categoria) and (busqueda.lower() in p['nombre'].lower()):
                with cols[i % 4]:
                    with st.container(border=True):
                        st.image(p.get('imagen_url') or "https://via.placeholder.com/150", use_container_width=True)
                        st.markdown(f"### {p['nombre']}")
                        color_s = "#ff5555" if p['stock'] <= 3 else "#50fa7b"
                        cs, cp = st.columns(2)
                        cs.markdown(f"Stock: <br><span style='color:{color_s}; font-size:22px; font-weight:bold;'>{p['stock']}</span>", unsafe_allow_html=True)
                        cp.markdown(f"Precio: <br><span style='font-size:22px; font-weight:bold;'>S/ {p['precio_venta']}</span>", unsafe_allow_html=True)
                        if st.button("REGISTRAR SALIDA", key=f"s_{p['id']}", use_container_width=True):
                            if p['stock'] > 0:
                                supabase.table("productos").update({"stock": p['stock']-1}).eq("id", p['id']).execute()
                                # Registro con usuario incluido
                                supabase.table("historial").insert({
                                    "producto_nombre":p['nombre'], 
                                    "cantidad":-1, 
                                    "usuario":st.session_state.user
                                }).execute()
                                st.rerun()
    else:
        st.info("No hay productos cargados en esta categoría.")

# 2. CARGA DE PRODUCTOS (OBLIGATORIA)
elif opcion == "Carga":
    st.header("➕ Ingreso de Mercancía Nueva")
    with st.form("form_carga", clear_on_submit=True):
        st.info("Nombre y Categoría son campos obligatorios.")
        n = st.text_input("Modelo / Repuesto *")
        c = st.selectbox("Categoría *", ["Pantallas", "Baterías", "Flex", "Glases", "Otros"])
        s = st.number_input("Stock Inicial", min_value=1, value=1)
        p = st.number_input("Precio en Soles (S/)", min_value=0.0, format="%.2f")
        img = st.text_input("Link de Imagen (URL)")
        if st.form_submit_button("GUARDAR EN VILLAFIX"):
            if not n or not c:
                st.error("Debes completar el nombre y la categoría.")
            else:
                supabase.table("productos").insert({"nombre":n, "categoria":c, "stock":s, "precio_venta":p, "imagen_url":img}).execute()
                st.success(f"Producto {n} registrado correctamente.")

# 3. ESTADÍSTICAS (GRÁFICOS) 
elif opcion == "Stats":
    st.header("📊 Estadísticas de Uso")
    h_data = supabase.table("historial").select("*").execute().data
    p_data = supabase.table("productos").select("*").execute().data
    
    col1, col2 = st.columns(2)
    with col1:
        if h_data:
            df_h = pd.DataFrame(h_data)
            salidas = df_h[df_h['cantidad'] < 0].groupby('producto_nombre')['cantidad'].sum().abs().reset_index()
            fig = px.bar(salidas.nlargest(10, 'cantidad'), x='producto_nombre', y='cantidad', title="Top 10 Repuestos más usados", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        if p_data:
            df_p = pd.DataFrame(p_data)
            fig_p = px.pie(df_p, names='categoria', values='stock', hole=0.4, title="Stock por Categoría", template="plotly_dark")
            st.plotly_chart(fig_p, use_container_width=True)

# 4. HISTORIAL (CORREGIDO)
elif opcion == "Log":
    st.markdown("<h1 style='color:#50fa7b;'>📜 HISTORIAL DE MOVIMIENTOS</h1>", unsafe_allow_html=True)
    res_logs = supabase.table("historial").select("*").order("fecha", desc=True).execute().data
    if res_logs:
        df_logs = pd.DataFrame(res_logs)
        df_logs['fecha'] = pd.to_datetime(df_logs['fecha']).dt.strftime('%d/%m/%Y %H:%M')
        df_logs = df_logs.rename(columns={'fecha':'FECHA','producto_nombre':'REPUESTO','cantidad':'U.','usuario':'USUARIO'})
        st.dataframe(df_logs[['FECHA', 'REPUESTO', 'U.', 'USUARIO']], use_container_width=True, hide_index=True)
    else:
        st.info("El historial está vacío.")

# 5. GESTIÓN DE USUARIOS
elif opcion == "Users":
    st.header("👤 Registro de Colaboradores")
    with st.form("nu"):
        un = st.text_input("Nuevo Usuario")
        pw = st.text_input("Contraseña")
        rl = st.selectbox("Rol", ["Normal", "Super"])
        if st.form_submit_button("CREAR ACCESO"):
            if un and pw:
                supabase.table("usuarios").insert({"usuario":un, "contrasena":pw, "rol":rl}).execute()
                st.success(f"Usuario {un} creado con éxito.")
            else:
                st.error("Campos vacíos.")

# 6. PROVEEDORES
elif opcion == "Prov":
    st.header("📞 Directorio de Proveedores")
    # (Aquí puedes poner la misma lógica de tabla o tarjetas para proveedores)
