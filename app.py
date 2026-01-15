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

# --- DISEÑO UI REFINADO (ALTA LEGIBILIDAD) ---
st.markdown("""
    <style>
    /* FONDO CLARO Y TEXTO OSCURO PARA EL ÁREA CENTRAL */
    .stApp { 
        background-color: #fcfcfc; 
        color: #1a1a1a !important; 
    }
    
    /* FORZAR COLOR DE LETRAS EN FORMULARIOS Y ETIQUETAS */
    label, p, span, .stMarkdown {
        color: #1a1a1a !important;
        font-weight: 500;
    }

    h1, h2, h3, h4 {
        color: #1a222b !important;
        font-weight: bold !important;
    }

    /* BARRA LATERAL (SE MANTIENE OSCURA SEGÚN LO ACORDADO) */
    [data-testid="stSidebar"] {
        background-color: #1a222b !important;
        color: white !important;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: white !important;
    }

    .profile-section {
        text-align: left;
        padding: 20px 0px 20px 20px;
        background: #1a222b;
    }
    .profile-pic {
        width: 85px; height: 85px; border-radius: 50%;
        border: 3px solid #f39c12; margin-bottom: 10px; object-fit: cover;
    }
    .profile-name { font-size: 16px; font-weight: bold; color: white !important; margin: 0; }
    .profile-status { font-size: 11px; color: #95a5a6 !important; margin-bottom: 5px; }

    .sidebar-divider {
        height: 1px; background-color: #3498db; margin: 5px 0 15px 0; width: 100%; opacity: 0.5;
    }

    .stSidebar .stButton>button {
        background-color: transparent; color: #bdc3c7; border: none;
        border-radius: 0; height: 48px; text-align: left; font-size: 14px;
        width: 100%; padding-left: 20px !important; transition: 0.2s;
    }
    .stSidebar .stButton>button:hover {
        background-color: #2c3e50 !important; color: white !important;
        border-left: 5px solid #3498db !important;
    }
    
    [data-testid="stSidebarNav"] {display: none;}

    /* INPUTS Y SELECTS CON BORDE MÁS OSCURO PARA QUE SE VEAN */
    input, select, textarea {
        border: 1px solid #ced4da !important;
        color: #1a1a1a !important;
    }
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
    with col_a: busqueda = st.text_input("Buscar modelo o repuesto", placeholder="Escriba aquí...")
    with col_b: categoria = st.selectbox("Filtrar por Apartado", ["Todos", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])

    items = supabase.table("productos").select("*").order("nombre").execute().data
    if items:
        cols = st.columns(4)
        for i, p in enumerate(items):
            if (categoria == "Todos" or p['categoria'] == categoria) and (busqueda.lower() in p['nombre'].lower()):
                with cols[i % 4]:
                    with st.container(border=True):
                        st.image(p.get('imagen_url') or "https://via.placeholder.com/150", use_column_width=True)
                        st.markdown(f"<p style='font-size: 16px; margin-bottom: 2px;'><b>{p['nombre']}</b></p>", unsafe_allow_html=True)
                        cs, cp = st.columns(2)
                        cs.markdown(f"<p style='color:#1a1a1a;'>U: {p['stock']}</p>", unsafe_allow_html=True)
                        cp.markdown(f"<p style='color:#1a1a1a;'>S/ {p['precio_venta']}</p>", unsafe_allow_html=True)
                        if st.button("SALIDA", key=f"s_{p['id']}", use_container_width=True):
                            if p['stock'] > 0:
                                supabase.table("productos").update({"stock": p['stock']-1}).eq("id", p['id']).execute()
                                supabase.table("historial").insert({"producto_nombre":p['nombre'], "cantidad":-1, "usuario":st.session_state.user}).execute()
                                st.rerun()

elif opcion == "Carga":
    st.markdown("<h2>📥 Añadir Producto</h2>", unsafe_allow_html=True)
    
    with st.form("form_carga", clear_on_submit=True):
        st.info("Complete los datos. Si el modelo ya existe, se sumará a las cantidades actuales.")
        
        n = st.text_input("Modelo / Repuesto *")
        c = st.selectbox("Categoría *", ["Seleccionar", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])
        s = st.number_input("Cantidad a añadir", min_value=1, step=1)
        p = st.number_input("Precio Venta (S/) *", min_value=0.0, step=0.50)
        img = st.text_input("URL Imagen (Opcional)")
        
        enviar = st.form_submit_button("CONSOLIDAR INGRESO", use_container_width=True)
        
        if enviar:
            errores = []
            if not n: errores.append("Modelo")
            if c == "Seleccionar": errores.append("Categoría")
            if p <= 0: errores.append("Precio")
            
            if errores:
                st.warning(f"⚠️ Falta completar: {', '.join(errores)}. Por favor, rellene todos los campos obligatorios.")
            else:
                existe = supabase.table("productos").select("*").eq("nombre", n).execute()
                if existe.data:
                    id_prod = existe.data[0]['id']
                    nuevo_stock = existe.data[0]['stock'] + s
                    supabase.table("productos").update({"stock": nuevo_stock, "precio_venta": p, "imagen_url": img}).eq("id", id_prod).execute()
                    st.success(f"✅ Stock actualizado. Total: {nuevo_stock}")
                else:
                    supabase.table("productos").insert({"nombre": n, "categoria": c, "stock": s, "precio_venta": p, "imagen_url": img}).execute()
                    st.success(f"✅ Nuevo producto '{n}' creado.")
                
                supabase.table("historial").insert({"producto_nombre": n, "cantidad": s, "usuario": st.session_state.user}).execute()

elif opcion == "Log":
    st.markdown("<h2>📜 Historial de Movimientos</h2>", unsafe_allow_html=True)
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
        fig = px.pie(df_p, names='categoria', values='stock', hole=0.4, title="Distribución de Stock")
        st.plotly_chart(fig, use_container_width=True)

elif opcion == "Users":
    st.markdown("<h2>👥 Gestión de Usuarios</h2>", unsafe_allow_html=True)
    with st.form("nu"):
        un = st.text_input("Usuario")
        pw = st.text_input("Clave")
        rl = st.selectbox("Rol", ["Normal", "Super"])
        if st.form_submit_button("CREAR ACCESO"):
            supabase.table("usuarios").insert({"usuario":un, "contrasena":pw, "rol":rl}).execute()
            st.success("Usuario creado.")

elif opcion == "Prov":
    st.markdown("<h2>📞 Proveedores</h2>", unsafe_allow_html=True)
    # Lógica de proveedores mantenida...
