import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VillaFix | System", page_icon="🛠️", layout="wide")

# --- DISEÑO UI REVOLUCIONARIO (VILLAFIX STYLE) ---
st.markdown("""
    <style>
    /* Fondo principal más elegante */
    .stApp { background-color: #0f172a; color: #f8fafc; }
    
    /* Menú lateral estilo Cuadros Sólidos */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        min-width: 280px !important;
    }
    
    /* Estilo para los botones del menú (Cuadros) */
    .stSidebar [data-testid="stWidgetLabel"] { display: none; }
    .stSidebar .stButton>button {
        background-color: #334155;
        color: white;
        border: none;
        border-radius: 12px;
        height: 80px;
        margin-bottom: 15px;
        font-size: 18px;
        font-weight: bold;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: 0.3s;
    }
    .stSidebar .stButton>button:hover {
        background-color: #38bdf8;
        color: #0f172a;
        transform: translateY(-3px);
        box-shadow: 0 10px 15px -3px rgba(56, 189, 248, 0.4);
    }

    /* Tarjetas de Producto Blancas */
    .product-card {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 20px;
        color: #1e293b;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
        margin-bottom: 25px;
    }
    
    /* Buscador e Inputs */
    .stTextInput>div>div>input {
        background-color: #1e293b;
        color: white;
        border: 1px solid #334155;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE NAVEGACIÓN (CUADROS) ---
if 'seccion' not in st.session_state:
    st.session_state.seccion = "Almacén"

with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#38bdf8;'>VillaFix</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:0.8em;'>SISTEMA DE GESTIÓN V1.0</p>", unsafe_allow_html=True)
    st.write("---")
    
    # Botones tipo Cuadro
    if st.button("📦 ALMACÉN"): st.session_state.seccion = "Almacén"
    if st.button("📊 ESTADÍSTICAS"): st.session_state.seccion = "Estadísticas"
    if st.button("➕ INGRESAR"): st.session_state.seccion = "Añadir"
    if st.button("🤝 PROVEEDORES"): st.session_state.seccion = "Proveedores"
    if st.button("📜 HISTORIAL"): st.session_state.seccion = "Historial"

# --- LÓGICA DE SECCIONES ---
seccion = st.session_state.seccion

if seccion == "Almacén":
    st.header(f"📦 Inventario Central")
    
    c1, c2 = st.columns([3, 1])
    with c1: busqueda = st.text_input("Buscar repuesto...", placeholder="Ej: iPhone 11")
    with c2: cat_filtro = st.selectbox("Categoría", ["Todos", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])

    # Consulta a DB
    query = supabase.table("productos").select("*").order("nombre")
    if cat_filtro != "Todos": query = query.eq("categoria", cat_filtro)
    res = query.execute().data

    if res:
        cols = st.columns(4)
        for idx, p in enumerate(res):
            if busqueda.lower() in p['nombre'].lower():
                with cols[idx % 4]:
                    # Card Visual
                    st.markdown(f'''
                    <div class="product-card">
                        <img src="{p.get('imagen_url') or 'https://via.placeholder.com/150'}" style="width:100%; border-radius:15px; height:140px; object-fit:cover; margin-bottom:10px;">
                        <div style="font-size:1.1em; font-weight:800; height:50px; overflow:hidden;">{p['nombre'].upper()}</div>
                        <div style="font-size:1.8em; font-weight:900; color:{'#ef4444' if p['stock'] <= 3 else '#10b981'}">{p['stock']} <span style="font-size:0.5em; color:#64748b;">u.</span></div>
                        <div style="font-size:1.3em; color:#1e293b; font-weight:600; margin-bottom:10px;">${p['precio_venta']}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    if st.button(f"REGISTRAR SALIDA", key=f"btn_{p['id']}", use_container_width=True):
                        if p['stock'] > 0:
                            supabase.table("productos").update({"stock": p['stock'] - 1}).eq("id", p['id']).execute()
                            supabase.table("historial").insert({"producto_nombre": p['nombre'], "cantidad": -1}).execute()
                            st.rerun()

elif seccion == "Estadísticas":
    st.header("📊 Inteligencia VillaFix")
    h_data = supabase.table("historial").select("*").execute().data
    if h_data:
        df_h = pd.DataFrame(h_data)
        salidas = df_h[df_h['cantidad'] < 0].groupby('producto_nombre')['cantidad'].sum().abs().reset_index()
        fig = px.bar(salidas.nlargest(8, 'cantidad'), x='producto_nombre', y='cantidad', 
                     title="Los 8 Repuestos más usados", template="plotly_dark", color_discrete_sequence=['#38bdf8'])
        st.plotly_chart(fig, use_container_width=True)

elif seccion == "Añadir":
    st.header("➕ Ingresar nuevo repuesto")
    with st.form("new_p"):
        n = st.text_input("Nombre")
        c = st.selectbox("Categoría", ["Pantallas", "Baterías", "Flex", "Glases", "Otros"])
        s = st.number_input("Stock", min_value=0)
        p = st.number_input("Precio", min_value=0.0)
        img = st.text_input("Link de imagen")
        if st.form_submit_button("GUARDAR EN VILLAFIX"):
            supabase.table("productos").insert({"nombre":n, "categoria":c, "stock":s, "precio_venta":p, "imagen_url":img}).execute()
            st.success("Guardado")

elif seccion == "Proveedores":
    st.header("🤝 Directorio")
    # ... código de proveedores similar al anterior ...

elif seccion == "Historial":
    st.header("📜 Logs de Movimientos")
    logs = supabase.table("historial").select("*").order("fecha", desc=True).limit(50).execute().data
    if logs:
        st.table(pd.DataFrame(logs))
