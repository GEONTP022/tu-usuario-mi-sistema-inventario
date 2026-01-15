import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="VillaFix | Admin", page_icon="🛠️", layout="wide")

# --- LÓGICA DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.rol = None
    st.session_state.user = None
    st.session_state.menu = "Stock"

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
                st.error("Error de conexión.")
    st.stop()

# --- CSS MAESTRO (CORRECCIÓN FINAL DE COLORES) ---
st.markdown("""
    <style>
    /* 1. FONDO BLANCO GLOBAL */
    .stApp, .main, .block-container {
        background-color: #ffffff !important;
    }

    /* 2. ETIQUETAS DEL FORMULARIO EN NEGRO (Modelo, Categoría...) */
    div[data-testid="stWidgetLabel"] p, label, .stMarkdown p, h1, h2, h3 {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 700 !important;
    }

    /* 3. ARREGLO ESPECÍFICO PARA EL STOCK (Tarjetas) */
    /* Forzamos que todo texto dentro de una tarjeta sea NEGRO... */
    div[data-testid="stVerticalBlockBorderWrapper"] div,
    div[data-testid="stVerticalBlockBorderWrapper"] p,
    div[data-testid="stVerticalBlockBorderWrapper"] span {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    
    /* ...EXCEPTO el texto dentro de los botones (SALIDA), que debe ser BLANCO */
    div[data-testid="stVerticalBlockBorderWrapper"] button p,
    div[data-testid="stVerticalBlockBorderWrapper"] button div {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* 4. INPUTS (Cajas de Texto) */
    input, textarea, .stNumberInput input {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        border: 1px solid #888 !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        border: 1px solid #888 !important;
    }
    div[data-baseweb="select"] span { color: #000000 !important; }
    ul[data-testid="stSelectboxVirtualDropdown"] li {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* 5. BARRA LATERAL (TEXTO BLANCO) */
    [data-testid="stSidebar"] { background-color: #1a222b !important; }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    /* Excepción: Botones del sidebar al pasar el mouse */
    [data-testid="stSidebar"] button:hover {
        background-color: rgba(255,255,255,0.1) !important;
        border-left: 4px solid #3498db !important;
    }

    /* 6. BOTONES DE ACCIÓN (AZULES) */
    div.stForm button, div[data-testid="column"] button {
        background-color: #2488bc !important;
        border: none !important;
    }
    /* Texto blanco forzado para botones generales */
    div.stForm button p {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    
    /* Botones Rojos de la zona de Reset */
    button[kind="secondary"] {
        background-color: #ff4b4b !important;
        color: white !important;
    }

    [data-testid="stSidebarNav"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# --- PANEL IZQUIERDO ---
with st.sidebar:
    st.markdown(f"""
        <div style="text-align:center; padding: 20px 0;">
            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" style="width:100px; height:100px; border-radius:50%; border:3px solid #f39c12; object-fit:cover; display:block; margin:0 auto 10px auto;">
            <p style="font-size:18px; font-weight:bold; margin:0; color:white !important;">{st.session_state.user.upper()}</p>
            <p style="font-size:12px; color:#f39c12 !important; margin:0;">{st.session_state.rol.upper()} USER</p>
        </div>
        <div style="height:1px; background-color:#3498db; opacity:0.3; margin-bottom:20px;"></div>
    """, unsafe_allow_html=True)
    
    if st.button("📊 Dashboard / Stock", use_container_width=True): st.session_state.menu = "Stock"
    
    if st.session_state.rol == "Super":
        if st.button("📥 Añadir Producto", use_container_width=True): st.session_state.menu = "Carga"
        if st.button("📋 Historial", use_container_width=True): st.session_state.menu = "Log"
        if st.button("📈 Estadísticas", use_container_width=True): st.session_state.menu = "Stats"
        if st.button("👥 Usuarios", use_container_width=True): st.session_state.menu = "Users"
        if st.button("📞 Proveedores", use_container_width=True): st.session_state.menu = "Prov"
        # OPCIÓN DE BORRADO
        if st.button("⚙️ Reset Sistema", use_container_width=True): st.session_state.menu = "Reset"

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# --- ÁREA CENTRAL ---
opcion = st.session_state.menu

if opcion == "Stock":
    st.markdown("<h2>Inventario General</h2>", unsafe_allow_html=True)
    col_a, col_b = st.columns([3, 1])
    with col_a: busqueda = st.text_input("Buscar por modelo", placeholder="Ej: Pantalla iPhone...")
    with col_b: categoria = st.selectbox("Apartado", ["Todos", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])

    items = supabase.table("productos").select("*").order("nombre").execute().data
    if items:
        cols = st.columns(4)
        for i, p in enumerate(items):
            if (categoria == "Todos" or p['categoria'] == categoria) and (busqueda.lower() in p['nombre'].lower()):
                with cols[i % 4]:
                    with st.container(border=True):
                        st.image(p.get('imagen_url') or "https://via.placeholder.com/150", use_column_width=True)
                        # Usamos estilos en línea con !important para asegurar visibilidad negra
                        st.markdown(f"<div style='text-align:center; color:#000000 !important; font-weight:bold; margin-bottom:5px; height:40px; overflow:hidden;'>{p['nombre']}</div>", unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        with c1: st.markdown(f"<div style='text-align:center; color:#000000 !important; font-size:13px;'>U: {p['stock']}</div>", unsafe_allow_html=True)
                        with c2: st.markdown(f"<div style='text-align:center; color:#000000 !important; font-size:13px;'>S/ {p['precio_venta']}</div>", unsafe_allow_html=True)
                        st.markdown("<div style='margin-top:5px;'></div>", unsafe_allow_html=True)
                        if st.button("SALIDA", key=f"s_{p['id']}", use_container_width=True):
                            if p['stock'] > 0:
                                supabase.table("productos").update({"stock": p['stock']-1}).eq("id", p['id']).execute()
                                supabase.table("historial").insert({"producto_nombre":p['nombre'], "cantidad":-1, "usuario":st.session_state.user}).execute()
                                st.rerun()

elif opcion == "Carga":
    st.markdown("<h2>📥 Añadir Producto</h2>", unsafe_allow_html=True)
    with st.form("form_carga", clear_on_submit=True):
        st.markdown("<p>Complete los campos obligatorios (*)</p>", unsafe_allow_html=True)
        
        n = st.text_input("Modelo / Repuesto *")
        c = st.selectbox("Categoría *", ["Seleccionar", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])
        s = st.number_input("Cantidad a añadir", min_value=1, step=1)
        p = st.number_input("Precio Venta (S/) *", min_value=0.0, step=0.5)
        img = st.text_input("URL Imagen (Opcional)")
        
        if st.form_submit_button("CONSOLIDAR INGRESO"):
            if not n or c == "Seleccionar" or p <= 0:
                st.warning("⚠️ Falta completar Nombre, Categoría o Precio.")
            else:
                existe = supabase.table("productos").select("*").eq("nombre", n).execute()
                if existe.data:
                    nuevo_stock = existe.data[0]['stock'] + s
                    supabase.table("productos").update({"stock": nuevo_stock, "precio_venta": p, "imagen_url": img}).eq("id", existe.data[0]['id']).execute()
                    st.success(f"✅ Stock actualizado!")
                else:
                    supabase.table("productos").insert({"nombre": n, "categoria": c, "stock": s, "precio_venta": p, "imagen_url": img}).execute()
                    st.success(f"✅ Creado!")
                supabase.table("historial").insert({"producto_nombre": n, "cantidad": s, "usuario": st.session_state.user}).execute()

elif opcion == "Log":
    st.markdown("<h2>📜 Historial</h2>", unsafe_allow_html=True)
    logs = supabase.table("historial").select("*").order("fecha", desc=True).execute().data
    if logs:
        df = pd.DataFrame(logs)
        df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m/%Y %H:%M')
        st.dataframe(df[['fecha', 'producto_nombre', 'cantidad', 'usuario']], use_container_width=True, hide_index=True)

elif opcion == "Stats":
    st.markdown("<h2>📊 Estadísticas</h2>", unsafe_allow_html=True)
    p_data = supabase.table("productos").select("*").execute().data
    if p_data:
        df_p = pd.DataFrame(p_data)
        fig = px.pie(df_p, names='categoria', values='stock', hole=0.4, title="Stock por Categoría")
        st.plotly_chart(fig, use_container_width=True)

elif opcion == "Users":
    st.markdown("<h2>👥 Usuarios</h2>", unsafe_allow_html=True)
    with st.form("nu"):
        un = st.text_input("Usuario")
        pw = st.text_input("Clave")
        rl = st.selectbox("Rol", ["Normal", "Super"])
        if st.form_submit_button("CREAR"):
            supabase.table("usuarios").insert({"usuario":un, "contrasena":pw, "rol":rl}).execute()
            st.success("Usuario creado.")

elif opcion == "Prov":
    st.markdown("<h2>📞 Proveedores</h2>", unsafe_allow_html=True)
    provs = supabase.table("proveedores").select("*").execute().data
    if provs:
        for pr in provs:
            with st.container(border=True):
                st.markdown(f"**{pr['nombre_contacto']}**")
                st.link_button("WhatsApp", f"https://wa.me/{pr['whatsapp']}")

# --- SECCIÓN DE RESET (SOLO PARA SUPER USUARIO) ---
elif opcion == "Reset":
    st.markdown("<h2>⚙️ Zona de Peligro</h2>", unsafe_allow_html=True)
    st.warning("⚠️ ADVERTENCIA: Estas acciones no se pueden deshacer.")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.error("Eliminar TODOS los Productos")
        if st.button("🗑️ BORRAR STOCK TOTAL", type="secondary", use_container_width=True):
            try:
                # Borrado seguro iterando IDs
                data = supabase.table("productos").select("id").execute().data
                for item in data:
                    supabase.table("productos").delete().eq("id", item['id']).execute()
                st.success("Inventario eliminado por completo.")
            except Exception as e:
                st.error(f"Error: {e}")

    with col_r2:
        st.error("Eliminar TODO el Historial")
        if st.button("🗑️ BORRAR HISTORIAL TOTAL", type="secondary", use_container_width=True):
            try:
                data = supabase.table("historial").select("id").execute().data
                for item in data:
                    supabase.table("historial").delete().eq("id", item['id']).execute()
                st.success("Historial eliminado por completo.")
            except Exception as e:
                st.error(f"Error: {e}")
