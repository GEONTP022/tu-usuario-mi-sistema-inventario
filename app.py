import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, date
import time

# --- CONEXIÓN ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except:
    st.error("⚠️ Error de conexión: Revisa tus 'secrets' de Streamlit.")
    st.stop()

st.set_page_config(page_title="VillaFix | Admin", page_icon="🛠️", layout="wide")

# --- LÓGICA DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.rol = None
    st.session_state.user = None
    st.session_state.menu = "Stock"

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align:center; color:#2488bc;'>VILLAFIX ACCESS</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
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

# --- FUNCIÓN DE BÚSQUEDA INTELIGENTE ---
def es_coincidencia(busqueda, texto_db):
    if not busqueda: return True 
    if not texto_db: return False
    
    b = str(busqueda).lower().strip()
    
    # Alias comunes
    if b.startswith("ip") and len(b) > 2 and b[2].isdigit(): 
        b = b.replace("ip", "iphone", 1)
    elif b == "ip":
        b = "iphone"

    b_nospace = b.replace(" ", "").replace("-", "")
    t = str(texto_db).lower()
    t_nospace = t.replace(" ", "").replace("-", "")
    
    if b in t: return True
    if b_nospace in t_nospace: return True
    return False

# --- CSS MAESTRO (EL DISEÑO BONITO, PERO SEGURO) ---
st.markdown("""
    <style>
    /* Fondo y Textos */
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #000000 !important; }
    div[data-testid="stMetricLabel"] p { color: #000000 !important; font-weight: bold; }
    div[data-testid="stMetricValue"] { color: #2488bc !important; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #1a222b; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    [data-testid="stSidebar"] button { 
        background-color: transparent !important; 
        border: none !important; 
        color: #bdc3c7 !important; 
        text-align: left !important; 
        padding-left: 20px !important; 
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] button:hover { 
        background-color: rgba(255,255,255,0.05) !important; 
        border-left: 4px solid #3498db !important; 
        color: #ffffff !important; 
    }

    /* Inputs */
    input, textarea, .stNumberInput input { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        border: 1px solid #888888 !important; 
    }
    input:disabled { background-color: #f0f2f6 !important; }

    /* TARJETAS DE PRODUCTO (Diseño Restaurado) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        padding: 15px !important;
        border-radius: 8px !important;
    }

    /* Imágenes */
    div[data-testid="stImage"] {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 10px;
        height: 150px; /* Altura fija para uniformidad */
    }
    div[data-testid="stImage"] img {
        object-fit: contain;
        max-height: 140px;
    }

    /* Botones */
    div.stButton button { 
        background-color: #2488bc !important; 
        color: #ffffff !important; 
        font-weight: bold !important; 
        border: none !important; 
        border-radius: 4px !important;
    }
    div.stButton button:disabled { 
        background-color: #e74c3c !important; 
        color: white !important; 
        opacity: 1 !important; 
    }

    /* Ocultar navegación default */
    [data-testid="stSidebarNav"] {display: none;}
    
    .profile-section { text-align: center !important; padding: 20px 0px; }
    .profile-pic { width: 90px; height: 90px; border-radius: 50%; border: 3px solid #f39c12; object-fit: cover; display: block; margin: 0 auto 10px auto; }
    </style>
    """, unsafe_allow_html=True)

# --- VENTANAS MODALES ---

@st.dialog("Gestionar Inventario")
def modal_gestion(producto):
    st.markdown(f"### {producto['nombre']}")
    tab_salida, tab_devolucion = st.tabs(["📉 SALIDA DE STOCK", "↩️ DEVOLUCIÓN / INGRESO"])
    
    with tab_salida:
        st.info(f"Stock Actual: {producto['stock']} unidades")
        try: techs = [t['nombre'] for t in supabase.table("tecnicos").select("nombre").execute().data]
        except: techs = ["General"]
        try: locs = [l['nombre'] for l in supabase.table("locales").select("nombre").execute().data]
        except: locs = ["Principal"]

        with st.form("form_salida_modal"):
            col1, col2 = st.columns(2)
            with col1: tecnico = st.selectbox("Técnico", ["Seleccionar"] + techs)
            with col2: local = st.selectbox("Local", ["Seleccionar"] + locs)
            
            max_val = producto['stock'] if producto['stock'] > 0 else 1
            cantidad = st.number_input("Cantidad a RETIRAR", min_value=1, max_value=max_val, step=1)
            
            if st.form_submit_button("CONFIRMAR SALIDA", use_container_width=True):
                if producto['stock'] <= 0:
                     st.error("⚠️ No hay stock para retirar.")
                elif tecnico == "Seleccionar" or local == "Seleccionar":
                    st.error("⚠️ Faltan datos.")
                else:
                    with st.spinner('Procesando...'):
                        nuevo_stock = producto['stock'] - cantidad
                        supabase.table("productos").update({"stock": nuevo_stock}).eq("id", producto['id']).execute()
                        supabase.table("historial").insert({
                            "producto_nombre": producto['nombre'], "cantidad": -cantidad,
                            "usuario": st.session_state.user, "tecnico": tecnico, "local": local
                        }).execute()
                        time.sleep(0.5)
                    st.success("✅ Salida registrada")
                    time.sleep(0.5)
                    st.rerun()

    with tab_devolucion:
        st.info("Use esto para devoluciones o ingresos rápidos.")
        with st.form("form_devolucion_modal"):
            razon = st.text_input("Motivo", value="Devolución")
            cant_dev = st.number_input("Cantidad a INGRESAR", min_value=1, step=1)
            
            if st.form_submit_button("CONFIRMAR INGRESO", use_container_width=True):
                with st.spinner('Procesando...'):
                    nuevo_stock_dev = producto['stock'] + cant_dev
                    supabase.table("productos").update({"stock": nuevo_stock_dev}).eq("id", producto['id']).execute()
                    supabase.table("historial").insert({
                        "producto_nombre": producto['nombre'], 
                        "cantidad": cant_dev,
                        "usuario": st.session_state.user, 
                        "tecnico": razon,
                        "local": "Almacén"
                    }).execute()
                    time.sleep(0.5)
                st.success("✅ Stock actualizado")
                time.sleep(0.5)
                st.rerun()

@st.dialog("✨ Nuevo Producto")
def modal_nuevo_producto():
    st.markdown("### Crear Producto")
    with st.form("form_nuevo_prod"):
        n = st.text_input("Nombre / Modelo *")
        col_cat, col_mar = st.columns(2)
        with col_cat: c = st.selectbox("Categoría *", ["Seleccionar", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])
        with col_mar: m = st.text_input("Marca")
        
        cb = st.text_input("Código de Batería (Si aplica)")
        s = st.number_input("Stock Inicial *", min_value=0, step=1)
        
        col_p1, col_p2 = st.columns(2)
        with col_p1: p_gen = st.number_input("Precio General (S/) *", min_value=0.0, step=0.5)
        with col_p2: p_punto = st.number_input("Precio Punto (S/)", min_value=0.0, step=0.5)
        
        img = st.text_input("URL Imagen (Opcional)")

        if st.form_submit_button("GUARDAR PRODUCTO", use_container_width=True):
            if not n or c == "Seleccionar" or p_gen <= 0:
                st.error("⚠️ Faltan datos obligatorios.")
            else:
                # --- VALIDACIÓN ROBUSTA ---
                # Solo bloquea si Nombre + Marca + Categoría + Código son IDÉNTICOS.
                query = supabase.table("productos").select("id")\
                    .eq("nombre", n).eq("marca", m).eq("categoria", c)
                
                if cb: query = query.eq("codigo_bateria", cb)
                else: query = query.eq("codigo_bateria", "") # Manejar vacíos

                existe = query.execute()

                if existe.data:
                    st.error("⚠️ Ya existe este producto EXACTO (Mismo nombre, marca y código).")
                else:
                    try:
                        with st.spinner('Guardando...'):
                            supabase.table("productos").insert({
                                "nombre": n, "categoria": c, "marca": m, "codigo_bateria": cb,
                                "stock": s, "precio_venta": p_gen, "precio_punto": p_punto, "imagen_url": img
                            }).execute()
                            
                            supabase.table("historial").insert({
                                "producto_nombre": n, "cantidad": s, "usuario": st.session_state.user,
                                "tecnico": "Ingreso Inicial", "local": "Almacén"
                            }).execute()
                        st.success("✅ Producto creado")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar. Verifica que la columna 'precio_punto' exista en Supabase. Detalles: {e}")

@st.dialog("⚠️ Confirmar Eliminación")
def modal_borrar_producto(producto):
    st.write(f"¿Estás seguro de eliminar **{producto['nombre']}**?")
    st.warning("Esta acción es irreversible.")
    if st.button("SÍ, ELIMINAR", type="primary", use_container_width=True):
        with st.spinner('Eliminando...'):
            supabase.table("productos").delete().eq("id", producto['id']).execute()
        st.success("✅ Eliminado")
        time.sleep(0.5)
        st.rerun()

@st.dialog("⚠️ Eliminar Técnico")
def modal_borrar_tecnico(nombre):
    st.write(f"¿Eliminar a {nombre}?")
    if st.button("SÍ, ELIMINAR"):
        supabase.table("tecnicos").delete().eq("nombre", nombre).execute()
        st.rerun()

@st.dialog("⚠️ Eliminar Local")
def modal_borrar_local(nombre):
    st.write(f"¿Eliminar local {nombre}?")
    if st.button("SÍ, ELIMINAR"):
        supabase.table("locales").delete().eq("nombre", nombre).execute()
        st.rerun()

# --- PANEL IZQUIERDO ---
with st.sidebar:
    st.markdown(f"""
        <div class="profile-section">
            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" class="profile-pic">
            <p style="font-size:18px; font-weight:bold; margin:0; color:white !important;">{st.session_state.user.upper()}</p>
            <p style="font-size:12px; color:#f39c12 !important; margin:0;">{st.session_state.rol.upper()} USER</p>
        </div>
        <div style="height:1px; background-color:#3498db; opacity:0.3; margin-bottom:20px;"></div>
    """, unsafe_allow_html=True)
    
    if st.button("📊 Dashboard / Stock", use_container_width=True): st.session_state.menu = "Stock"
    if st.session_state.rol == "Super":
        if st.button("📥 Añadir Producto", use_container_width=True): st.session_state.menu = "Carga"
        if st.button("📋 Historial", use_container_width=True): st.session_state.menu = "Log"
        if st.button("📈 Estadísticas", use_container_width=True): st.session_state.menu = "Stats"
        if st.button("👥 Usuarios / Config", use_container_width=True): st.session_state.menu = "Users"
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
    with col_a: 
        busqueda = st.text_input("Buscar...", placeholder="Ej: ip11, Samsung, celda...")
    with col_b: 
        categoria = st.selectbox("Apartado", ["Todos", "⚠️ Solo Bajo Stock", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])

    items = supabase.table("productos").select("*").order("nombre").execute().data
    if items:
        # Filtrado
        filtered_items = []
        for p in items:
            coincide_nombre = es_coincidencia(busqueda, p['nombre'])
            coincide_marca = es_coincidencia(busqueda, p.get('marca'))
            coincide_codigo = es_coincidencia(busqueda, p.get('codigo_bateria'))
            match_busqueda = coincide_nombre or coincide_marca or coincide_codigo
            
            if categoria == "⚠️ Solo Bajo Stock":
                match_categoria = (p['stock'] <= 2)
            elif categoria == "Todos":
                match_categoria = True
            else:
                match_categoria = (p['categoria'] == categoria)
                
            if match_busqueda and match_categoria:
                filtered_items.append(p)
        
        if busqueda:
            b_clean = busqueda.lower().strip()
            filtered_items.sort(key=lambda x: 0 if x['nombre'].lower().startswith(b_clean) else 1)

        # --- GRID SYSTEM ROBUSTO (CLAVE PARA QUE NO SE ROMPA) ---
        # Dividimos en filas de 4 columnas. Esto es lo que arregla el error visual.
        N_COLS = 4
        rows = [filtered_items[i:i + N_COLS] for i in range(0, len(filtered_items), N_COLS)]
        
        for row in rows:
            cols = st.columns(N_COLS)
            for i, p in enumerate(row):
                with cols[i]:
                    with st.container(border=True):
                        # Imagen (con protección contra errores)
                        img_url = p.get('imagen_url')
                        if not img_url: img_url = "https://via.placeholder.com/150"
                        
                        st.markdown(f"""
                            <div style="display: flex; justify-content: center; align-items: center; height: 160px; width: 100%; margin-bottom: 10px;">
                                <img src="{img_url}" style="max-height: 150px; width: auto; object-fit: contain; display: block;">
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Info
                        marca_val = p.get('marca', '')
                        marca_html = f"<div style='color:#555; font-size:11px; font-weight:bold; text-transform:uppercase;'>{marca_val}</div>" if marca_val else "<div style='height:16px;'></div>"
                        
                        cod_bat = p.get('codigo_bateria')
                        cod_html = f"<div style='color:#555; font-size:11px; font-weight:bold; text-transform:uppercase; margin-top:2px;'>{cod_bat}</div>" if cod_bat else ""
                        
                        st.markdown(f"""
                            <div style="text-align:center; height:90px; display:flex; flex-direction:column; justify-content:flex-start; align-items:center;">
                                {marca_html}
                                <div style="color:black; font-weight:bold; font-size:15px; line-height:1.2; margin-top:2px;">{p['nombre']}</div>
                                {cod_html}
                            </div>
                        """, unsafe_allow_html=True)

                        # Precios
                        c1, c2, c3 = st.columns([1, 1.2, 1.2])
                        with c1: 
                            st.markdown(f"<div style='text-align:center; color:black; font-size:12px; font-weight:bold;'>Stock<br><span style='font-size:14px;'>{p['stock']}</span></div>", unsafe_allow_html=True)
                        with c2: 
                            st.markdown(f"<div style='text-align:center; color:#2c3e50; font-size:12px;'>Gral.<br><span style='font-weight:bold;'>S/ {p['precio_venta']}</span></div>", unsafe_allow_html=True)
                        with c3:
                            p_punto = p.get('precio_punto', 0)
                            color_punto = "#27ae60" if p_punto else "#bdc3c7"
                            val_str = f"S/ {p_punto}" if p_punto else "--"
                            st.markdown(f"<div style='text-align:center; color:{color_punto}; font-size:12px;'>Punto<br><span style='font-weight:bold;'>{val_str}</span></div>", unsafe_allow_html=True)
                        
                        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                        
                        if p['stock'] > 0:
                            if st.button("SALIDA", key=f"s_{p['id']}", use_container_width=True): modal_gestion(p)
                        else:
                            st.button("🚫 NO STOCK", key=f"ns_{p['id']}", disabled=True, use_container_width=True)

elif opcion == "Carga":
    st.markdown("<h2>📥 Gestión de Stock</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c2:
        if st.button("➕ NUEVO PRODUCTO", use_container_width=True): modal_nuevo_producto()
    
    all_products = supabase.table("productos").select("*").order("nombre").execute().data
    opciones = {f"{p['nombre']} ({p.get('marca','')})": p for p in all_products}
    
    seleccion = st.selectbox("Buscar para editar/reponer:", ["Seleccionar"] + list(opciones.keys()))
    
    if seleccion != "Seleccionar":
        prod = opciones[seleccion]
        with st.container(border=True):
            st.markdown(f"### Editando: {prod['nombre']}")
            with st.form("form_update_stock"):
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    new_cat = st.selectbox("Categoría", ["Pantallas", "Baterías", "Flex", "Glases", "Otros"], index=["Pantallas", "Baterías", "Flex", "Glases", "Otros"].index(prod['categoria']))
                    new_marca = st.text_input("Marca", value=prod.get('marca', ''))
                    new_cod = st.text_input("Código Batería", value=prod.get('codigo_bateria', ''))
                with col_u2:
                    new_p_gen = st.number_input("Precio Gral (S/)", value=float(prod['precio_venta']), step=0.5)
                    # Protección por si la columna no existe
                    val_punto = float(prod.get('precio_punto') or 0.0)
                    new_p_punto = st.number_input("Precio Punto (S/)", value=val_punto, step=0.5)
                    new_img = st.text_input("Imagen URL", value=prod.
