import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px # Para los gráficos

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="CELLTECH PRO | Gestión", 
    page_icon="🛠️", 
    layout="wide"
)

# --- CONEXIÓN SUPABASE ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- ESTILO GENERAL (MATERIAL DESIGN SUEVE) ---
st.markdown("""
    <style>
    .stApp { background-color: #26292F; color: #E0E0E0; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1E2024;
        color: #E0E0E0;
        box-shadow: 2px 0px 5px rgba(0,0,0,0.2);
    }
    .stRadio > label { font-size: 1.1em; }
    
    /* Botones de Categorías */
    .stButton>button {
        background-color: #3B4048;
        color: #B0B7C0;
        border: none;
        border-radius: 8px;
        padding: 10px 15px;
        font-weight: bold;
        transition: all 0.2s ease;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3), -2px -2px 5px rgba(60,60,60,0.1);
    }
    .stButton>button:hover {
        background-color: #4A5059;
        color: #FFFFFF;
        box-shadow: 3px 3px 7px rgba(0,0,0,0.4), -3px -3px 7px rgba(60,60,60,0.15);
    }
    
    /* Tarjetas de Producto */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #2F333A;
        border: none !important;
        border-radius: 12px !important;
        padding: 15px;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.4), -4px -4px 10px rgba(60,60,60,0.1);
        transition: all 0.2s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 6px 6px 15px rgba(0,0,0,0.5), -6px -6px 15px rgba(60,60,60,0.15);
    }
    
    /* Estilo del Buscador */
    .stTextInput>div>div>input {
        background-color: #2F333A;
        border: 1px solid #4A5059;
        color: #E0E0E0;
        border-radius: 8px;
        box-shadow: inset 2px 2px 5px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN LATERAL ---
with st.sidebar:
    st.image("https://i.imgur.com/mi_logo.png", width=150) # Reemplaza con tu logo
    st.title("CELLTECH PRO")
    st.markdown("---")
    menu_seleccionado = st.radio(
        "Navegación",
        ["📦 Almacén", "📊 Dashboard", "➕ Nuevo Producto", "👥 Proveedores", "📜 Registro"],
        icons=["box", "graph-up", "plus-circle", "people", "clipboard-data"]
    )

# --- FUNCIÓN PARA CARGAR PRODUCTOS ---
@st.cache_data(ttl=60) # Cacha los datos por 60 segundos para evitar recargar mucho
def get_productos():
    return supabase.table("productos").select("*").order("nombre").execute().data

# --- PÁGINA: ALMACÉN ---
if menu_seleccionado == "📦 Almacén":
    st.header("📦 Inventario y Salidas")
    
    col_bus, col_cat_filtros = st.columns([3, 1])
    
    with col_bus:
        busqueda = st.text_input("Buscar por nombre o modelo...", placeholder="Ej: Pantalla iPhone 11", key="search_alm")
    
    with col_cat_filtros:
        categorias_db = ["Pantallas", "Baterías", "Flex", "Glases", "Otros"] # Puedes obtener esto dinámicamente de tu DB
        categoria_elegida = st.selectbox("Filtrar por Categoría", ["Todas"] + categorias_db)
    
    productos = get_productos()
    
    productos_filtrados = []
    if productos:
        for p in productos:
            if (categoria_elegida == "Todas" or p['categoria'] == categoria_elegida) and \
               (busqueda.lower() in p['nombre'].lower()):
                productos_filtrados.append(p)

    if productos_filtrados:
        st.subheader(f"Total de ítems: {len(productos_filtrados)}")
        cols = st.columns(4) # Mostrar 4 productos por fila
        
        for i, p in enumerate(productos_filtrados):
            with cols[i % 4]: # Asegura que cada producto vaya a su columna
                with st.container(border=True):
                    # --- IMAGEN DEL PRODUCTO ---
                    if p.get('imagen_url') and p['imagen_url'].strip():
                        st.image(p['imagen_url'], width=150, use_column_width="auto")
                    else:
                        st.image("https://via.placeholder.com/150x150?text=No+Image", width=150, use_column_width="auto") # Placeholder
                    
                    st.markdown(f"**{p['nombre']}**")
                    
                    # --- STOCK CON ALERTA VISUAL ---
                    color_stock = "red" if p['stock'] <= 3 else "green"
                    st.markdown(f"Stock: <span style='color:{color_stock}; font-weight:bold;'>{p['stock']}</span>", unsafe_allow_html=True)
                    st.write(f"Precio: ${p['precio_venta']:.2f}")
                    
                    # --- BOTÓN DE SALIDA ---
                    if st.button(f"Sacar (-1)", key=f"out_{p['id']}", use_container_width=True):
                        if p['stock'] > 0:
                            supabase.table("productos").update({"stock": p['stock'] - 1}).eq("id", p['id']).execute()
                            supabase.table("historial").insert({"producto_nombre": p['nombre'], "cantidad": -1}).execute()
                            st.cache_data.clear() # Limpia la caché para recargar datos
                            st.rerun()
                        else:
                            st.error("¡Stock agotado!")
    else:
        st.info("No hay productos que coincidan con los filtros o la búsqueda.")

# --- PÁGINA: DASHBOARD DE ESTADÍSTICAS ---
elif menu_seleccionado == "📊 Dashboard":
    st.header("📊 Resumen de Actividad")
    
    historial_data = supabase.table("historial").select("*").execute().data
    productos_data = supabase.table("productos").select("nombre, stock").execute().data

    if historial_data:
        df_historial = pd.DataFrame(historial_data)
        
        st.subheader("Movimientos Recientes")
        st.dataframe(df_historial.head(10).style.format({'fecha': lambda x: pd.to_datetime(x).strftime('%d/%m %H:%M')}))

        # Gráfico de Productos más Salidos (ventas)
        salidas = df_historial[df_historial['cantidad'] < 0] # Solo salidas
        if not salidas.empty:
            top_salidas = salidas.groupby('producto_nombre')['cantidad'].sum().abs().nlargest(5)
            df_top_salidas = top_salidas.reset_index(name='Total Salidas')
            
            fig_salidas = px.bar(df_top_salidas, x='producto_nombre', y='Total Salidas', 
                                 title='Top 5 Productos Más Salidos', 
                                 labels={'producto_nombre': 'Producto', 'Total Salidas': 'Unidades Vendidas'},
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_salidas, use_container_width=True)
        else:
            st.info("Aún no hay suficientes salidas para generar un gráfico.")

    if productos_data:
        df_productos = pd.DataFrame(productos_data)
        
        st.subheader("Stock Actual")
        fig_stock = px.pie(df_productos, values='stock', names='nombre', 
                           title='Distribución de Stock por Producto',
                           color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_stock, use_container_width=True)


# --- PÁGINA: NUEVO PRODUCTO ---
elif menu_seleccionado == "➕ Nuevo Producto":
    st.header("➕ Agregar Nuevo Repuesto")
    
    with st.form("form_nuevo_producto", clear_on_submit=True):
        nombre = st.text_input("Nombre del Repuesto", placeholder="Ej: Pantalla iPhone 13 Pro Max OLED")
        categoria = st.selectbox("Categoría", ["Pantallas", "Baterías", "Flex", "Glases", "Otros"])
        stock_inicial = st.number_input("Stock Inicial", min_value=0, value=1)
        precio_venta = st.number_input("Precio de Venta Unitario", min_value=0.00, value=0.00, format="%.2f")
        imagen_url = st.text_input("URL de la Imagen (opcional)", placeholder="Pega el link de la imagen aquí")
        
        if st.form_submit_button("Registrar Producto"):
            if nombre and categoria:
                supabase.table("productos").insert({
                    "nombre": nombre,
                    "categoria": categoria,
                    "stock": stock_inicial,
                    "precio_venta": precio_venta,
                    "imagen_url": imagen_url if imagen_url else None
                }).execute()
                st.success(f"Producto '{nombre}' agregado correctamente.")
                st.cache_data.clear() # Limpia la caché para ver el nuevo producto
                st.rerun()
            else:
                st.error("Por favor, completa al menos el nombre y la categoría.")

# --- PÁGINA: PROVEEDORES ---
elif menu_seleccionado == "👥 Proveedores":
    st.header("👥 Gestión de Proveedores")

    with st.expander("📝 Añadir Nuevo Proveedor"):
        with st.form("form_nuevo_proveedor", clear_on_submit=True):
            nombre_contacto = st.text_input("Nombre del Contacto")
            empresa = st.text_input("Nombre de la Empresa")
            whatsapp = st.text_input("Número de WhatsApp (Ej: +54911xxxxxxxx)")
            notas = st.text_area("Notas Adicionales")
            
            if st.form_submit_button("Guardar Proveedor"):
                if nombre_contacto and empresa:
                    supabase.table("proveedores").insert({
                        "nombre_contacto": nombre_contacto,
                        "empresa": empresa,
                        "whatsapp": whatsapp,
                        "notas": notas
                    }).execute()
                    st.success(f"Proveedor '{empresa}' registrado.")
                    st.rerun()
                else:
                    st.error("Por favor, completa el nombre del contacto y la empresa.")

    st.subheader("Lista de Proveedores")
    proveedores_data = supabase.table("proveedores").select("*").execute().data

    if proveedores_data:
        for p in proveedores_data:
            with st.container(border=True):
                col_info, col_btn = st.columns([3, 1])
                col_info.markdown(f"**{p['empresa']}** - *{p['nombre_contacto']}*")
                col_info.write(f"Notas: {p['notas'] if p['notas'] else 'N/A'}")
                if p['whatsapp']:
                    col_btn.link_button("WhatsApp", f"https://wa.me/{p['whatsapp'].replace('+', '')}")
    else:
        st.info("Aún no hay proveedores registrados.")

# --- PÁGINA: REGISTRO (HISTORIAL) ---
elif menu_seleccionado == "📜 Registro":
    st.header("📜 Historial de Movimientos")
    
    historial_data = supabase.table("historial").select("*").order("fecha", desc=True).limit(100).execute().data
    
    if historial_data:
        df_historial = pd.DataFrame(historial_data)
        df_historial['fecha'] = pd.to_datetime(df_historial['fecha']).dt.strftime('%d/%m/%Y %H:%M:%S')
        st.dataframe(df_historial, use_container_width=True)
    else:
        st.info("No hay registros de movimientos aún.")
