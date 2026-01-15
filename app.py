import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="VillaFix | System", page_icon="🛠️", layout="wide")

# --- DISEÑO UI PREMIUM (BLOQUES SÓLIDOS) ---
st.markdown("""
    <style>
    /* Fondo Midnight de alta gama */
    .stApp { background-color: #0f172a; color: #f8fafc; }
    
    /* Panel Izquierdo (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 2px solid #334155;
        min-width: 300px !important;
    }
    
    /* Botones tipo CUADRO SÓLIDO */
    .stSidebar .stButton>button {
        background-color: #334155;
        color: #94a3b8;
        border: none;
        border-radius: 15px;
        height: 100px; /* Cuadros grandes */
        margin-bottom: 20px;
        font-size: 16px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.3s all ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    
    /* Efecto al pasar el mouse o estar activo */
    .stSidebar .stButton>button:hover, .stSidebar .stButton>button:active {
        background-color: #38bdf8;
        color: #0f172a;
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
    }

    /* Tarjetas de Producto Blancas con borde redondeado suave */
    .product-card {
        background-color: #ffffff;
        border-radius: 25px;
        padding: 25px;
        color: #1e293b;
        text-align: center;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 30px;
    }
    
    /* Buscador Moderno */
    .stTextInput>div>div>input {
        background-color: #1e293b;
        color: white;
        border: 2px solid #334155;
        border-radius: 15px;
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE NAVEGACIÓN ---
if 'seccion' not in st.session_state:
    st.session_state.seccion = "INICIO"

with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#38bdf8; font-size:45px; margin-bottom:0;'>VillaFix</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#64748b; margin-bottom:30px;'>SOLUCIONES TÉCNICAS</p>", unsafe_allow_html=True)
    
    # Botones en formato de Cuadros
    if st.button("🏠 INICIO / STOCK"): st.session_state.seccion = "INICIO"
    if st.button("📈 REPORTES"): st.session_state.seccion = "REPORTES"
    if st.button("📥 NUEVO INGRESO"): st.session_state.seccion = "NUEVO"
    if st.button("📞 PROVEEDORES"): st.session_state.seccion = "PROVEEDORES"
    if st.button("🕒 HISTORIAL"): st.session_state.seccion = "HISTORIAL"

# --- LÓGICA DE SECCIONES ---
seccion = st.session_state.seccion

if seccion == "INICIO":
    st.markdown("<h2 style='color:#38bdf8;'>📦 ALMACÉN CENTRAL</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([3, 1])
    with c1: busqueda = st.text_input("", placeholder="🔍 Buscar repuesto o modelo...")
    with c2: cat_filtro = st.selectbox("CATEGORÍA", ["TODOS", "PANTALLAS", "BATERÍAS", "FLEX", "GLASES", "OTROS"])

    # Consulta a DB
    query = supabase.table("productos").select("*").order("nombre")
    if cat_filtro != "TODOS": query = query.eq("categoria", cat_filtro.capitalize())
    res = query.execute().data

    if res:
        cols = st.columns(4)
        for idx, p in enumerate(res):
            if busqueda.lower() in p['nombre'].lower():
                with cols[idx % 4]:
                    st.markdown(f'''
                    <div class="product-card">
                        <img src="{p.get('imagen_url') or 'https://via.placeholder.com/150'}" style="width:100%; border-radius:20px; height:150px; object-fit:cover; margin-bottom:15px;">
                        <div style="font-size:1.1em; font-weight:800; color:#0f172a; height:45px; overflow:hidden;">{p['nombre'].upper()}</div>
                        <div style="font-size:2em; font-weight:900; margin:10px 0; color:{'#ef4444' if p['stock'] <= 3 else '#10b981'}">{p['stock']} <span style="font-size:0.4em; color:#94a3b8;">STOCK</span></div>
                        <div style="font-size:1.4em; color:#334155; font-weight:700;">${p['precio_venta']}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    if st.button(f"REGISTRAR SALIDA", key=f"btn_{p['id']}", use_container_width=True):
                        if p['stock'] > 0:
                            supabase.table("productos").update({"stock": p['stock'] - 1}).eq("id", p['id']).execute()
                            supabase.table("historial").insert({"producto_nombre": p['nombre'], "cantidad": -1}).execute()
                            st.rerun()

elif seccion == "REPORTES":
    st.header("📊 Inteligencia de Ventas")
    # Aquí van los cuadros de plotly que vimos antes
    h_data = supabase.table("historial").select("*").execute().data
    if h_data:
        df = pd.DataFrame(h_data)
        salidas = df[df['cantidad'] < 0].groupby('producto_nombre')['cantidad'].sum().abs().reset_index()
        fig = px.bar(salidas.nlargest(10, 'cantidad'), x='producto_nombre', y='cantidad', color_discrete_sequence=['#38bdf8'], template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# ... (El resto de secciones se mantienen con esta estética)
