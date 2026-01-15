import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="VillaFix | Inventario", page_icon="🛠️", layout="wide")

# --- DISEÑO UI ---
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

# --- PANEL IZQUIERDO ---
if 'menu' not in st.session_state: st.session_state.menu = "Stock"

with st.sidebar:
    st.markdown("<h1 style='color:#50fa7b; text-align:center;'>VillaFix</h1>", unsafe_allow_html=True)
    st.write("---")
    st.markdown('<p class="sidebar-header">📦 Gestión de Almacén</p>', unsafe_allow_html=True)
    if st.button("🖼️ Ver Inventario", use_container_width=True): st.session_state.menu = "Stock"
    if st.button("➕ Ingreso de Mercancía", use_container_width=True): st.session_state.menu = "Carga"
    
    st.markdown('<p class="sidebar-header">🔄 Operaciones</p>', unsafe_allow_html=True)
    if st.button("📜 Historial de Salidas", use_container_width=True): st.session_state.menu = "Log"
    if st.button("📊 Estadísticas de Uso", use_container_width=True): st.session_state.menu = "Stats"
    
    st.markdown('<p class="sidebar-header">👥 Directorio</p>', unsafe_allow_html=True)
    if st.button("📞 Proveedores", use_container_width=True): st.session_state.menu = "Prov"

# --- LÓGICA DE NAVEGACIÓN ---
opcion = st.session_state.menu

# 1. INVENTARIO GENERAL
if opcion == "Stock":
    st.markdown("<h1 style='color:#50fa7b;'>INVENTARIO GENERAL - VILLAFIX</h1>", unsafe_allow_html=True)
    col_a, col_b = st.columns([3, 1])
    with col_a: busqueda = st.text_input("", placeholder="🔍 Buscar por modelo o repuesto...")
    with col_b: categoria = st.selectbox("Filtrar", ["Todos", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])

    query = supabase.table("productos").select("*").order("nombre")
    if categoria != "Todos": query = query.eq("categoria", categoria)
    items = query.execute().data

    if items:
        cols = st.columns(4)
        for i, p in enumerate(items):
            if busqueda.lower() in p['nombre'].lower():
                with cols[i % 4]:
                    with st.container(border=True):
                        st.image(p.get('imagen_url') or "https://via.placeholder.com/150", use_container_width=True)
                        st.markdown(f"### {p['nombre']}")
                        color_stock = "#ff5555" if p['stock'] <= 3 else "#50fa7b"
                        c_stock, c_precio = st.columns(2)
                        c_stock.markdown(f"Stock: <br><span style='color:{color_stock}; font-size:22px; font-weight:bold;'>{p['stock']}</span>", unsafe_allow_html=True)
                        c_precio.markdown(f"Precio: <br><span style='font-size:22px; font-weight:bold;'>S/ {p['precio_venta']}</span>", unsafe_allow_html=True)
                        if st.button(f"REGISTRAR SALIDA", key=f"btn_{p['id']}", use_container_width=True):
                            if p['stock'] > 0:
                                supabase.table("productos").update({"stock": p['stock'] - 1}).eq("id", p['id']).execute()
                                supabase.table("historial").insert({"producto_nombre": p['nombre'], "cantidad": -1}).execute()
                                st.rerun()

# 2. AÑADIR PRODUCTOS (OBLIGATORIO)
elif opcion == "Carga":
    st.header("➕ Ingreso de Mercancía Nueva")
    with st.form("form_carga"):
        st.write("Complete los campos. *Nombre y Categoría son obligatorios*.")
        nombre_new = st.text_input("Modelo / Nombre del Repuesto *")
        cat_new = st.selectbox("Categoría *", ["Pantallas", "Baterías", "Flex", "Glases", "Otros"])
        stock_new = st.number_input("Cantidad inicial", min_value=1, value=1)
        precio_new = st.number_input("Precio de Venta (S/)", min_value=0.0, format="%.2f")
        img_new = st.text_input("Link de Imagen (URL)")
        
        btn_guardar = st.form_submit_button("GUARDAR EN VILLAFIX")
        
        if btn_guardar:
            if not nombre_new or not cat_new:
                st.error("Error: El nombre y la categoría son obligatorios.")
            else:
                supabase.table("productos").insert({
                    "nombre": nombre_new, "categoria": cat_new, 
                    "stock": stock_new, "precio_venta": precio_new, "imagen_url": img_new
                }).execute()
                st.success(f"Producto {nombre_new} añadido correctamente.")

# 3. ESTADÍSTICAS (GRÁFICOS)
elif opcion == "Stats":
    st.header("📊 Estadísticas de Uso y Stock")
    
    # Datos de Historial (Salidas)
    h_data = supabase.table("historial").select("*").execute().data
    p_data = supabase.table("productos").select("*").execute().data
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("🔥 Repuestos más usados")
        if h_data:
            df_h = pd.DataFrame(h_data)
            salidas = df_h[df_h['cantidad'] < 0].groupby('producto_nombre')['cantidad'].sum().abs().reset_index()
            fig_bar = px.bar(salidas.nlargest(10, 'cantidad'), x='producto_nombre', y='cantidad', 
                             color='cantidad', template="plotly_dark", labels={'cantidad':'Unidades'})
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with col_g2:
        st.subheader("📦 Distribución por Categoría")
        if p_data:
            df_p = pd.DataFrame(p_data)
            fig_pie = px.pie(df_p, names='categoria', values='stock', hole=0.4, template="plotly_dark")
            st.plotly_chart(fig_pie, use_container_width=True)

# 4. LOGS Y PROVEEDORES (Se mantienen simples)
elif opcion == "Log":
    st.header("📜 Historial de Salidas")
    logs = supabase.table("historial").select("*").order("fecha", desc=True).limit(50).execute().data
    if logs: st.table(pd.DataFrame(logs))
elif opcion == "Prov":
    st.header("📞 Directorio de Proveedores")
    # ... código de proveedores ...
