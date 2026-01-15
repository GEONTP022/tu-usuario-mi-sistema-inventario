import streamlit as st
from supabase import create_client

# Conexión
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Gestión de Repuestos Pro", layout="wide")

# --- MENÚ LATERAL ---
st.sidebar.title("🛠️ Panel de Control")
modo = st.sidebar.radio("Ir a:", ["📦 Inventario y Salidas", "➕ Agregar Nuevo Repuesto", "📜 Historial de Movimientos"])

# --- MÓDULO 1: INVENTARIO Y SALIDAS ---
if modo == "📦 Inventario y Salidas":
    st.title("📱 Almacén de Repuestos")
    
    busqueda = st.text_input("🔍 Buscar por modelo o tipo...", "").lower()
    
    col_central, col_derecha = st.columns([3, 1])

    with col_derecha:
        st.subheader("Apartados")
        if st.button("🔄 TODO", use_container_width=True): st.session_state.filtro = None
        for cat in ["Pantallas", "Baterías", "Flex", "Glases"]:
            if st.button(cat.upper(), use_container_width=True): st.session_state.filtro = cat

    with col_central:
        filtro = st.session_state.get('filtro')
        query = supabase.table("productos").select("*").order("nombre")
        if filtro: query = query.eq("categoria", filtro)
        
        res = query.execute()
        
        for p in res.data:
            if busqueda in p['nombre'].lower():
                # Alerta de color si hay poco stock
                color = "red" if p['stock'] <= 3 else "green"
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.markdown(f"### {p['nombre']}")
                    c2.markdown(f"Stock: :{color}[**{p['stock']}**]")
                    
                    if c3.button(f"Registrar Salida", key=f"out_{p['id']}"):
                        if p['stock'] > 0:
                            # 1. Descontar Stock
                            supabase.table("productos").update({"stock": p['stock'] - 1}).eq("id", p['id']).execute()
                            # 2. Guardar en Historial
                            supabase.table("historial").insert({"producto_nombre": p['nombre'], "cantidad": -1}).execute()
                            st.success(f"Salida de {p['nombre']} registrada")
                            st.rerun()
                        else:
                            st.error("Sin Stock disponible")

# --- MÓDULO 2: AGREGAR NUEVO ---
elif modo == "➕ Agregar Nuevo Repuesto":
    st.title("➕ Cargar Mercancía")
    with st.form("nuevo_producto"):
        nombre = st.text_input("Nombre del Repuesto (ej: Pantalla iPhone 13 GX)")
        categoria = st.selectbox("Categoría", ["Pantallas", "Baterías", "Flex", "Glases", "Otros"])
        stock_inicial = st.number_input("Stock Inicial", min_value=1, value=1)
        precio = st.number_input("Precio de Venta", min_value=0.0)
        
        if st.form_submit_button("Guardar en Almacén"):
            supabase.table("productos").insert({
                "nombre": nombre, "categoria": categoria, "stock": stock_inicial, "precio_venta": precio
            }).execute()
            st.success("¡Producto agregado con éxito!")

# --- MÓDULO 3: HISTORIAL ---
elif modo == "📜 Historial de Movimientos":
    st.title("📜 Registro de Actividad")
    hist = supabase.table("historial").select("*").order("fecha", desc=True).limit(50).execute()
    if hist.data:
        st.table(hist.data)
    else:
        st.info("Aún no hay movimientos registrados.")
