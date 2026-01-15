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

# --- DISEÑO UI REFORZADO (BLOQUEO DE MODO OSCURO) ---
st.markdown("""
    <style>
    /* 1. FORZAR FONDO BLANCO ABSOLUTO */
    .stApp, .main, .block-container, div[data-testid="stForm"] { 
        background-color: #ffffff !important; 
    }
    
    /* 2. FORZAR TEXTO NEGRO INTENSO EN TODO EL CONTENIDO CENTRAL */
    /* Títulos, etiquetas, párrafos y texto dentro de botones */
    .main h1, .main h2, .main h3, .main label, .main p, .main span, .main b, .main strong, .main div {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important; /* Fuerza extra para Safari/iOS */
        opacity: 1 !important;
    }

    /* 3. ARREGLO DE INPUTS Y DESPLEGABLES (Categorías) */
    /* Aseguramos fondo gris claro y letras negras para que se lea al escribir */
    input, select, textarea, div[data-baseweb="select"] > div {
        background-color: #f1f3f4 !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border: 2px solid #000000 !important;
    }

    /* Opciones dentro del menú desplegable */
    div[role="listbox"] ul li {
        color: #000000 !important;
        background-color: #ffffff !important;
    }

    /* 4. BARRA LATERAL OSCURA (Mantiene el perfil centrado) */
    [data-testid="stSidebar"] { background-color: #1a222b !important; }
    .profile-section { text-align: center !important; padding: 30px 10px; width: 100%; }
    .profile-pic { width: 100px; height: 100px; border-radius: 50%; border: 4px solid #f39c12; margin-bottom: 15px; object-fit: cover; display: block; margin-left: auto; margin-right: auto; }
    .profile-name { font-size: 19px; font-weight: bold; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; margin: 0; }
    .profile-status { font-size: 12px; color: #f39c12 !important; -webkit-text-fill-color: #f39c12 !important; margin-bottom: 5px; }
    .sidebar-divider { height: 1px; background-color: #3498db; margin: 10px 0 20px 0; width: 100%; opacity: 0.5; }
    
    /* Botones del sidebar siempre blancos */
    [data-testid="stSidebar"] button p { 
        color: #ffffff !important; 
        -webkit-text-fill-color: #ffffff !important; 
        font-size: 15px !important; 
    }

    /* 5. BOTÓN CONSOLIDAR INGRESO (Siempre azul, letra blanca) */
    div.stForm button {
        background-color: #2488bc !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: bold !important;
        border: none !important;
        height: 48px !important;
        opacity: 1 !important;
        width: 100% !important;
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
        <div class="sidebar-divider"></div>
    """, unsafe_allow_html=True)
    
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
    with col_a: busqueda = st.text_input("Buscar por modelo", placeholder="Ej: iPhone 13...")
    with col_b: categoria = st.selectbox("Apartado", ["Todos", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])

    items = supabase.table("productos").select("*").order("nombre").execute().data
    if items:
        cols = st.columns(4)
        for i, p in enumerate(items):
            if (categoria == "Todos" or p['categoria'] == categoria) and (busqueda.lower() in p['nombre'].lower()):
                with cols[i % 4]:
                    with st.container(border=True):
                        st.image(p.get('imagen_url') or "https://via.placeholder.com/150", use_column_width=True)
                        st.markdown(f"<p style='margin-bottom:0px; color:black;'><b>{p['nombre']}</b></p>", unsafe_allow_html=True)
                        cs, cp = st.columns(2)
                        cs.write(f"U: {p['stock']}")
                        cp.write(f"S/ {p['precio_venta']}")
                        if st.button("SALIDA", key=f"s_{p['id']}", use_container_width=True):
                            if p['stock'] > 0:
                                supabase.table("productos").update({"stock": p['stock']-1}).eq("id", p['id']).execute()
                                supabase.table("historial").insert({"producto_nombre":p['nombre'], "cantidad":-1, "usuario":st.session_state.user}).execute()
                                st.rerun()

elif opcion == "Carga":
    st.markdown("<h2>Añadir Producto</h2>", unsafe_allow_html=True)
    with st.form("form_carga", clear_on_submit=True):
        st.write("Complete los campos obligatorios (*)")
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
    st.markdown("<h2>Historial</h2>", unsafe_allow_html=True)
    logs = supabase.table("historial").select("*").order("fecha", desc=True).execute().data
    if logs:
        df = pd.DataFrame(logs)
        df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m/%Y %H:%M')
        st.dataframe(df[['fecha', 'producto_nombre', 'cantidad', 'usuario']], use_container_width=True, hide_index=True)

elif opcion == "Stats":
    st.markdown("<h2>Estadísticas</h2>", unsafe_allow_html=True)
    p_data = supabase.table("productos").select("*").execute().data
    if p_data:
        df_p = pd.DataFrame(p_data)
        fig = px.pie(df_p, names='categoria', values='stock', hole=0.4, title="Stock por Categoría")
        st.plotly_chart(fig, use_container_width=True)

elif opcion == "Users":
    st.markdown("<h2>Usuarios</h2>", unsafe_allow_html=True)
    with st.form("nu"):
        un = st.text_input("Usuario")
        pw = st.text_input("Clave")
        rl = st.selectbox("Rol", ["Normal", "Super"])
        if st.form_submit_button("CREAR"):
            supabase.table("usuarios").insert({"usuario":un, "contrasena":pw, "rol":rl}).execute()
            st.success("Usuario creado.")
