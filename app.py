import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="VillaFix | Inventario", page_icon="🛠️", layout="wide")

# --- DISEÑO UI REORGANIZADO ---
st.markdown("""
    <style>
    .stApp { background-color: #1e1e2f; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #11111b; min-width: 250px !important; }
    
    /* Estilo de los encabezados del menú lateral */
    .sidebar-header {
        font-size: 13px;
        color: #6272a4;
        font-weight: bold;
        margin-top: 25px;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    /* Tarjetas de Producto Modernas */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #282a36 !important;
        border: 1px solid #44475a !important;
        border-radius: 15px !important;
        padding: 20px !important;
        transition: 0.3s;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #50fa7b !important;
        transform: translateY(-5px);
    }

    /* Botón de Salida */
    .stButton>button {
        background-color: #ff5555;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        margin-top: 10px;
    }
    .stButton>button:hover {
        background-color: #ff6e6e;
        color: white;
        box-shadow: 0 0 15px rgba(255, 85, 85, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- PANEL IZQUIERDO: CLASIFICACIÓN LÓGICA ---
if 'menu' not in st.session_state: st.session_state.menu = "Stock"

with st.sidebar:
    st.markdown("<h1 style='color:#50fa7b; text-align:center;'>VillaFix</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # SECCIÓN 1: ALMACÉN
    st.markdown('<p class="sidebar-header">📦 Gestión de Almacén</p>', unsafe_allow_html=True)
    if st.button("🖼️ Ver Inventario", use_container_width=True): st.session_state.menu = "Stock"
    if st.button("➕ Ingreso de Mercancía", use_container_width=True): st.session_state.menu = "Carga"
    
    # SECCIÓN 2: MOVIMIENTOS
    st.markdown('<p class="sidebar-header">🔄 Operaciones</p>', unsafe_allow_html=True)
    if st.button("📜 Historial de Salidas", use_container_width=True): st.session_state.menu = "Log"
    if st.button("📊 Estadísticas de Uso", use_container_width=True): st.session_state.menu = "Stats"
    
    # SECCIÓN 3: CONTACTOS
    st.markdown('<p class="sidebar-header">👥 Directorio</p>', unsafe_allow_html=True)
    if st.button("📞 Proveedores", use_container_width=True): st.session_state.menu = "Prov"

# --- ÁREA CENTRAL ---
opcion = st.session_state.menu

if opcion == "Stock":
    st.markdown("<h1 style='color:#50fa7b;'>INVENTARIO GENERAL - VILLAFIX</h1>", unsafe_allow_html=True)
    
    # Buscador y Filtros
    col_a, col_b = st.columns([3, 1])
    with col_a: 
        busqueda = st.text_input("", placeholder="🔍 Buscar por modelo o repuesto...", key="search_bar")
    with col_b: 
        categoria = st.selectbox("Apartado", ["Todos", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])

    # Carga de datos
    query = supabase.table("productos").select("*").order("nombre")
    if categoria != "Todos": query = query.eq("categoria", categoria)
    items = query.execute().data

    if items:
        # Mostramos los productos en columnas de 4
        cols = st.columns(4)
        for i, p in enumerate(items):
            if busqueda.lower() in p['nombre'].lower():
                with cols[i % 4]:
                    with st.container(border=True):
                        # Imagen
                        img_url = p.get('imagen_url') if p.get('imagen_url') else "https://via.placeholder.com/150"
                        st.image(img_url, use_container_width=True)
                        
                        # Info del producto
                        st.markdown(f"### {p['nombre']}")
                        color_stock = "#ff5555" if p['stock'] <= 3 else "#50fa7b"
                        
                        # Datos en columnas pequeñas dentro de la tarjeta
                        c_stock, c_precio = st.columns(2)
                        c_stock.markdown(f"Stock: <br><span style='color:{color_stock}; font-size:22px; font-weight:bold;'>{p['stock']}</span>", unsafe_allow_html=True)
                        c_precio.markdown(f"Precio: <br><span style='font-size:22px; font-weight:bold;'>${p['precio_venta']}</span>", unsafe_allow_html=True)
                        
                        # BOTÓN DE REGISTRO DE SALIDA
                        if st.button(f"REGISTRAR SALIDA", key=f"btn_{p['id']}", use_container_width=True):
                            if p['stock'] > 0:
                                nuevo_stock = p['stock'] - 1
                                # Actualizar DB
                                supabase.table("productos").update({"stock": nuevo_stock}).eq("id", p['id']).execute()
                                # Guardar Log
                                supabase.table("historial").insert({
                                    "producto_nombre": p['nombre'], 
                                    "cantidad": -1
                                }).execute()
                                st.success(f"Salida de {p['nombre']}")
                                st.rerun()
                            else:
                                st.error("Sin stock")
    else:
        st.info("No hay productos cargados en esta categoría.")

elif opcion == "Log":
    st.header("📜 Historial de Salidas")
    logs = supabase.table("historial").select("*").order("fecha", desc=True).limit(50).execute().data
    if logs:
        st.table(pd.DataFrame(logs))
    else:
        st.info("No hay movimientos registrados.")

# ... (Las demás secciones se pueden ir completando igual)
