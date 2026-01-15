import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="CellMaster Pro", page_icon="📱", layout="wide")

# --- DISEÑO UI PROFESIONAL ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; color: #333; }
    [data-testid="stSidebar"] { background-color: #1e293b; color: white; }
    
    /* Tarjetas de Producto Elegantes */
    .product-card {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Botones de Categoría */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: 0.3s;
    }
    
    /* Títulos y Metricas */
    h1, h2, h3 { color: #1e293b; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN ---
with st.sidebar:
    st.title("🚀 CellMaster")
    menu = st.radio("MENÚ PRINCIPAL", ["Almacén", "Estadísticas", "Añadir Producto", "Proveedores", "Historial"])

# --- MÓDULO: ALMACÉN ---
if menu == "Almacén":
    st.header("📦 Inventario Real-Time")
    
    c1, c2 = st.columns([3, 1])
    with c1: busqueda = st.text_input("🔍 Buscar repuesto...", placeholder="Ej: Pantalla iPhone 11")
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
                    st.markdown(f'''
                    <div class="product-card">
                        <img src="{p.get('imagen_url') or 'https://via.placeholder.com/150'}" style="width:100%; border-radius:10px; height:150px; object-fit:cover; margin-bottom:10px;">
                        <div style="font-size:1.1em; font-weight:bold;">{p['nombre']}</div>
                        <div style="color:#64748b; font-size:0.9em; margin:5px 0;">{p['categoria']}</div>
                        <div style="font-size:1.5em; font-weight:800; color:{'#ef4444' if p['stock'] <= 3 else '#10b981'}">{p['stock']} <span style="font-size:0.5em; color:#94a3b8;">u.</span></div>
                        <div style="font-size:1.2em; font-weight:600; color:#1e293b;">${p['precio_venta']}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    if st.button(f"REGISTRAR SALIDA", key=f"btn_{p['id']}", use_container_width=True):
                        if p['stock'] > 0:
                            supabase.table("productos").update({"stock": p['stock'] - 1}).eq("id", p['id']).execute()
                            supabase.table("historial").insert({"producto_nombre": p['nombre'], "cantidad": -1}).execute()
                            st.rerun()
    else:
        st.info("No hay productos cargados en esta categoría.")

# --- MÓDULO: ESTADÍSTICAS ---
elif menu == "Estadísticas":
    st.header("📊 Inteligencia de Negocio")
    
    # Datos para cuadros
    h_data = supabase.table("historial").select("*").execute().data
    p_data = supabase.table("productos").select("nombre, stock").execute().data

    if h_data:
        df_h = pd.DataFrame(h_data)
        st.subheader("🔥 Lo que más sale (Top Ventas)")
        # Solo negativos (salidas)
        salidas = df_h[df_h['cantidad'] < 0].groupby('producto_nombre')['cantidad'].sum().abs().reset_index()
        fig = px.bar(salidas.nlargest(5, 'cantidad'), x='producto_nombre', y='cantidad', 
                     color='cantidad', labels={'cantidad':'Unidades', 'producto_nombre':'Producto'},
                     template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    if p_data:
        df_p = pd.DataFrame(p_data)
        st.subheader("📦 Distribución de Almacén")
        fig_pie = px.pie(df_p, values='stock', names='nombre', hole=.4)
        st.plotly_chart(fig_pie, use_container_width=True)

# --- MÓDULO: AÑADIR PRODUCTO ---
elif menu == "Añadir Producto":
    st.header("➕ Nuevo Ingreso")
    with st.form("new_form"):
        n = st.text_input("Nombre del Repuesto")
        c = st.selectbox("Categoría", ["Pantallas", "Baterías", "Flex", "Glases", "Otros"])
        s = st.number_input("Stock Inicial", min_value=0)
        p = st.number_input("Precio Venta", min_value=0.0)
        img = st.text_input("Link de la Imagen (URL)")
        if st.form_submit_button("GUARDAR EN NUBE"):
            supabase.table("productos").insert({"nombre":n, "categoria":c, "stock":s, "precio_venta":p, "imagen_url":img}).execute()
            st.success("Guardado correctamente")

# --- MÓDULO: PROVEEDORES ---
elif menu == "Proveedores":
    st.header("📞 Directorio de Proveedores")
    with st.expander("Añadir Proveedor"):
        with st.form("prov"):
            nom = st.text_input("Empresa/Contacto")
            tel = st.text_input("WhatsApp (ej: 54911...)")
            if st.form_submit_button("Añadir"):
                supabase.table("proveedores").insert({"nombre_contacto":nom, "whatsapp":tel}).execute()
    
    provs = supabase.table("proveedores").select("*").execute().data
    for pr in provs:
        with st.container(border=True):
            col1, col2 = st.columns([3,1])
            col1.write(f"**{pr['nombre_contacto']}**")
            col2.link_button("WhatsApp", f"https://wa.me/{pr['whatsapp']}")
