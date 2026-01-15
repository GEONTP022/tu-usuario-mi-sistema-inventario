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

# --- CSS MAESTRO (SOLUCIÓN VISUAL COMPLETA) ---
st.markdown("""
    <style>
    /* =========================================
       1. FORZAR MODO CLARO EN EL ÁREA PRINCIPAL
       ========================================= */
    :root {
        --primary-color: #2488bc;
        --background-color: #ffffff;
        --secondary-background-color: #f0f2f6;
        --text-color: #000000;
        --font: "sans-serif";
    }

    /* Fondo blanco absoluto para la zona de trabajo */
    .stApp, .main, .block-container {
        background-color: #ffffff !important;
    }

    /* TEXTOS NEGROS OBLIGATORIOS (Títulos, etiquetas, párrafos) */
    .main h1, .main h2, .main h3, .main p, .main span, .main div, .main label {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 600 !important;
    }

    /* Corrección específica para que 'Modelo', 'Categoría' se vean */
    div[data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
    }
    
    label[data-testid="stWidgetLabel"] p {
        color: #000000 !important;
        font-size: 14px !important;
    }

    /* INPUTS (Cajas de texto): Fondo blanco, Borde negro, Texto negro */
    input, textarea, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border-color: #000000 !important;
    }

    /* =========================================
       2. BARRA LATERAL (SIDEBAR) ESTILO PREMIUM
       ========================================= */
    [data-testid="stSidebar"] {
        background-color: #1a222b !important;
    }
    
    /* Perfil Centrado */
    .profile-section {
        text-align: center !important;
        padding: 20px 10px;
        margin-bottom: 10px;
    }
    .profile-pic {
        width: 90px; height: 90px; 
        border-radius: 50%; 
        border: 3px solid #f39c12; 
        object-fit: cover;
        display: block; margin: 0 auto 10px auto;
    }
    .profile-name { color: #ffffff !important; font-size: 18px; font-weight: bold; margin: 0; }
    .profile-status { color: #f39c12 !important; font-size: 12px; margin: 0; }

    /* BOTONES DEL MENÚ: Transparentes y limpios (COMO ANTES) */
    .stSidebar .stButton>button {
        background-color: transparent !important; /* Sin fondo de caja */
        color: #bdc3c7 !important;                /* Texto gris claro */
        border: none !important;                  /* Sin bordes */
        text-align: left !important;
        padding-left: 15px !important;
        font-size: 15px !important;
        transition: all 0.3s ease;
        box-shadow: none !important;
    }

    /* Efecto al pasar el mouse: Se vuelven blancos y brillantes */
    .stSidebar .stButton>button:hover {
        color: #ffffff !important;
        background-color: rgba(255,255,255,0.05) !important; /* Sutil fondo */
        padding-left: 20px !important; /* Pequeño desplazamiento a la derecha */
        border-left: 4px solid #3498db !important; /* Línea azul elegante */
    }
    
    /* Texto dentro de los botones del sidebar siempre visible */
    .stSidebar p {
        color: inherit !important;
    }

    /* =========================================
       3. BOTÓN DE ACCIÓN (AZUL SÓLIDO)
       ========================================= */
    div.stForm button {
        background-color: #2488bc !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%;
    }

    [data-testid="stSidebarNav"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# --- PANEL IZQUIERDO (SIDEBAR) ---
with st.sidebar:
    st.markdown(f"""
        <div class="profile-section">
            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" class="profile-pic">
            <p class="profile-name">{st.session_state.user.upper()}</p>
            <p class="profile-status">{st.session_state.rol.upper()} USER</p>
        </div>
        <div style="height: 1px; background: #3498db; opacity: 0.3; margin-bottom: 20px;"></div>
    """, unsafe_allow_html=True)
    
    # Botones limpios (sin cajas)
    if st.button("📊 Dashboard / Stock", use_container_width=True): st.session_state.menu = "Stock"
    
    if st.session_state.rol == "Super":
        if st.button("📥 Añadir Producto", use_container_width=True): st.session_state.menu = "Carga"
        if st.button("📋 Historial", use_container_width=True): st.session_state.menu = "Log"
        if st.button("📈 Estadísticas", use_container_width=True): st.session_state.menu = "Stats"
        if st.button("👥 Usuarios", use_container_width=True): st.session_state.menu = "Users"
        if st.button("📞 Proveedores", use_container_width=True): st.session_state.menu = "Prov"

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
                        st.markdown(f"<p style='margin:0; color:black;'><b>{p['nombre']}</b></p>", unsafe_allow_html=True)
                        cs, cp = st.columns(2)
                        cs.write(f"U: {p['stock']}")
                        cp.write(f"S/ {p['precio_venta']}")
                        if st.button("SALIDA", key=f"s_{p['id']}", use_container_width=True):
                            if p['stock'] > 0:
                                supabase.table("productos").update({"stock": p['stock']-1}).eq("id", p['id']).execute()
                                supabase.table("historial").insert({"producto_nombre":p['nombre'], "cantidad":-1, "usuario":st.session_state.user}).execute()
                                st.rerun()

elif opcion == "Carga":
    st.markdown("<h2>📥 Añadir Producto</h2>", unsafe_allow_html=True)
    with st.form("form_carga", clear_on_submit=True):
        st.markdown("<p style='color:black;'>Complete los campos obligatorios (*)</p>", unsafe_allow_html=True)
        
        # Estos campos ahora tendrán etiquetas NEGRAS forzadas
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
