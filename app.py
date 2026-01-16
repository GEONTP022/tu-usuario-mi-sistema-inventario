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
    st.error("⚠️ Error crítico de conexión. Verifique secrets.")
    st.stop()

st.set_page_config(page_title="VillaFix | Admin", page_icon="🛠️", layout="wide")

# --- LÓGICA DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.rol = None
    st.session_state.user = None
    st.session_state.menu = "Stock"

if not st.session_state.autenticado:
    st.markdown("<br><br><h1 style='text-align:center; color:#2488bc;'>VILLAFIX SYSTEM</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        with st.container(border=True):
            st.markdown("<h3 style='text-align:center;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.button("INGRESAR", use_container_width=True):
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

# --- FUNCIÓN DE BÚSQUEDA AVANZADA ---
def es_coincidencia(busqueda, texto_db):
    if not busqueda: return True 
    if not texto_db: return False
    
    # 1. Normalizar
    b = str(busqueda).lower().strip()
    
    # 2. Alias Inteligentes
    if b.startswith("ip") and len(b) > 2 and b[2].isdigit(): 
        b = b.replace("ip", "iphone", 1)
    elif b == "ip":
        b = "iphone"

    # 3. Comprimir espacios
    b_nospace = b.replace(" ", "").replace("-", "")
    t = str(texto_db).lower()
    t_nospace = t.replace(" ", "").replace("-", "")
    
    # 4. Comparar
    if b in t: return True
    if b_nospace in t_nospace: return True
    return False

# --- CSS MAESTRO RESTAURADO (ESTILO ORIGINAL) ---
st.markdown("""
    <style>
    /* Fondo y estructura */
    .stApp, .main, .block-container { background-color: #ffffff !important; }
    [data-testid="stSidebar"] { background-color: #1a222b !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
    
    /* Botones del Sidebar */
    [data-testid="stSidebar"] button { background-color: transparent !important; border: none !important; color: #bdc3c7 !important; text-align: left !important; padding-left: 15px !important; transition: 0.3s; }
    [data-testid="stSidebar"] button:hover { background-color: rgba(255,255,255,0.05) !important; border-left: 4px solid #3498db !important; color: #ffffff !important; padding-left: 20px !important; }
    
    /* Textos Generales (Forzar Negro) */
    div[data-testid="stWidgetLabel"] p, label, .stMarkdown p, h1, h2, h3, .stDialog p, .stDialog label, div[role="dialog"] p, .stMetriclabel { color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-weight: 700 !important; }
    div[data-testid="stMetricValue"] { color: #2488bc !important; -webkit-text-fill-color: #2488bc !important; }
    
    /* Inputs y Selects */
    input, textarea, .stNumberInput input { background-color: #ffffff !important; color: #000000 !important; -webkit-text-fill-color: #000000 !important; border: 1px solid #888888 !important; caret-color: #000000 !important; }
    input:disabled { background-color: #e9ecef !important; color: #555555 !important; -webkit-text-fill-color: #555555 !important; }
    div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #000000 !important; border: 1px solid #888888 !important; }
    div[data-baseweb="select"] span { color: #000000 !important; -webkit-text-fill-color: #000000 !important; }
    ul[data-testid="stSelectboxVirtualDropdown"] { background-color: #ffffff !important; }
    ul[data-testid="stSelectboxVirtualDropdown"] li { background-color: #ffffff !important; color: #000000 !important; }
    ul[data-testid="stSelectboxVirtualDropdown"] li:hover { background-color: #f0f2f6 !important; }
    
    /* Modal */
    div[role="dialog"] { background-color: #ffffff !important; color: #000000 !important; }
    
    /* Contenedores de Tarjetas (Restaurado el diseño, pero flex seguro) */
    div[data-testid="stVerticalBlockBorderWrapper"] { 
        background-color: #ffffff !important; 
        border: 1px solid #ddd !important; 
        padding: 10px !important; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important; 
        height: 100% !important; /* Altura 100% para igualar filas */
        min-height: 340px !important; 
        display: flex; 
        flex-direction: column; 
        justify-content: space-between; 
    }
    
    /* Imágenes */
    div[data-testid="stImage"] { display: flex !important; justify-content: center !important; align-items: center !important; width: 100% !important; margin: 0 auto !important; height: 160px !important; }
    div[data-testid="stImage"] img { display: block !important; margin-left: auto !important; margin-right: auto !important; max-height: 150px !important; width: auto !important; object-fit: contain !important; }
    
    /* Botones */
    div.stButton button { background-color: #2488bc !important; color: #ffffff !important; border: none !important; font-weight: bold !important; width: 100% !important; margin-top: auto !important; }
    div.stButton button p { color: #ffffff !important; }
    div.stButton button:disabled, button[kind="secondary"] { background-color: #e74c3c !important; color: white !important; opacity: 1 !important; border: 1px solid #c0392b !important; }
    div.stButton button:disabled p { color: white !important; }
    
    /* Extras */
    button[data-baseweb="tab"] { color: #000000 !important; }
    div[data-baseweb="tab-list"] { background-color: #f1f3f4 !important; border-radius: 8px; }
    .profile-section { text-align: center !important; padding: 20px 0px; }
    .profile-pic { width: 100px; height: 100px; border-radius: 50%; border: 3px solid #f39c12; object-fit: cover; display: block; margin: 0 auto 10px auto; }
    [data-testid="stSidebarNav"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# --- VENTANAS FLOTANTES (MODALES COMPLETOS) ---

@st.dialog("Gestionar Inventario")
def modal_gestion(producto):
    st.markdown(f"<h3 style='color:black;'>{producto['nombre']}</h3>", unsafe_allow_html=True)
    tab_salida, tab_devolucion = st.tabs(["📉 REGISTRAR SALIDA", "↩️ DEVOLUCIÓN / INGRESO"])
    
    with tab_salida:
        st.markdown(f"**Stock Actual:** {producto['stock']}")
        try: techs = [t['nombre'] for t in supabase.table("tecnicos").select("nombre").execute().data]
        except: techs = ["General"]
        try: locs = [l['nombre'] for l in supabase.table("locales").select("nombre").execute().data]
        except: locs = ["Principal"]

        with st.form("form_salida_modal"):
            col1, col2 = st.columns(2)
            with col1: tecnico = st.selectbox("Técnico", ["Seleccionar"] + techs, key="tec_sal")
            with col2: local = st.selectbox("Local", ["Seleccionar"] + locs, key="loc_sal")
            
            max_val = producto['stock'] if producto['stock'] > 0 else 1
            cantidad = st.number_input("Cantidad a RETIRAR", min_value=1, max_value=max_val, step=1, key="cant_sal")
            
            if st.form_submit_button("CONFIRMAR SALIDA"):
                if producto['stock'] <= 0:
                     st.error("⚠️ No hay stock para retirar.")
                elif tecnico == "Seleccionar" or local == "Seleccionar":
                    st.error("⚠️ Faltan datos.")
                else:
                    with st.spinner('Procesando salida...'):
                        nuevo_stock = producto['stock'] - cantidad
                        supabase.table("productos").update({"stock": nuevo_stock}).eq("id", producto['id']).execute()
                        supabase.table("historial").insert({
                            "producto_nombre": producto['nombre'], "cantidad": -cantidad,
                            "usuario": st.session_state.user, "tecnico": tecnico, "local": local
                        }).execute()
                        time.sleep(1)
                    st.success("✅ ¡Listo!")
                    time.sleep(0.5)
                    st.rerun()

    with tab_devolucion:
        st.info("Use esto para devoluciones de técnicos o ingresos rápidos.")
        with st.form("form_devolucion_modal"):
            razon = st.text_input("Motivo (Ej: Devolución Técnico, Error)", value="Devolución")
            cant_dev = st.number_input("Cantidad a INGRESAR/DEVOLVER", min_value=1, step=1, key="cant_dev")
            
            if st.form_submit_button("CONFIRMAR DEVOLUCIÓN"):
                with st.spinner('Procesando devolución...'):
                    nuevo_stock_dev = producto['stock'] + cant_dev
                    supabase.table("productos").update({"stock": nuevo_stock_dev}).eq("id", producto['id']).execute()
                    supabase.table("historial").insert({
                        "producto_nombre": producto['nombre'], 
                        "cantidad": cant_dev,
                        "usuario": st.session_state.user, 
                        "tecnico": razon,
                        "local": "Almacén"
                    }).execute()
                    time.sleep(1)
                st.success("✅ ¡Listo!")
                time.sleep(0.5)
                st.rerun()

@st.dialog("✨ Nuevo Producto")
def modal_nuevo_producto():
    st.markdown("<h3 style='color:black;'>Crear Producto</h3>", unsafe_allow_html=True)
    with st.form("form_nuevo_prod"):
        n = st.text_input("Nombre / Modelo *")
        
        c1, c2 = st.columns(2)
        with c1: c = st.selectbox("Categoría *", ["Seleccionar", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])
        with c2: m = st.text_input("Marca (Solo si aplica)")
        
        cb = st.text_input("Código de Batería (Solo para Baterías)")
        s = st.number_input("Stock Inicial *", min_value=0, step=1)
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            p_gen = st.number_input("Precio General (S/) *", min_value=0.0, step=0.5)
        with col_p2:
            p_punto = st.number_input("Precio Punto (S/)", min_value=0.0, step=0.5)
        
        img = st.text_input("URL Imagen (Opcional)")

        if st.form_submit_button("GUARDAR"):
            if not n or c == "Seleccionar" or p_gen <= 0:
                st.error("⚠️ Datos incompletos.")
            else:
                # --- VALIDACIÓN CORREGIDA ---
                # Solo bloquea si Nombre + Marca + Categoría + Código son IGUALES
                # Si el código es igual pero el modelo es distinto, PERMITE CREAR.
                
                query = supabase.table("productos").select("id")\
                    .eq("nombre", n)\
                    .eq("marca", m)\
                    .eq("categoria", c)
                
                # Manejo de código vacío o lleno
                if cb: query = query.eq("codigo_bateria", cb)
                else: query = query.eq("codigo_bateria", "")

                existe_dupla = query.execute()

                if existe_dupla.data:
                    st.error("⚠️ Ya existe este producto EXACTO (Mismo Nombre, Marca y Código).")
                else:
                    try:
                        with st.spinner('Creando producto...'):
                            supabase.table("productos").insert({
                                "nombre": n, "categoria": c, "marca": m, "codigo_bateria": cb,
                                "stock": s, "precio_venta": p_gen, "precio_punto": p_punto, "imagen_url": img
                            }).execute()
                            supabase.table("historial").insert({
                                "producto_nombre": n, "cantidad": s, "usuario": st.session_state.user,
                                "tecnico": "Ingreso Inicial", "local": "Almacén"
                            }).execute()
                            time.sleep(1)
                        st.success("✅ ¡Listo!")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error Base de Datos: {e}. ¿Creaste la columna 'precio_punto' en la tabla productos?")

@st.dialog("⚠️ Confirmar Eliminación")
def modal_borrar_producto(producto):
    st.write(f"¿Estás seguro de eliminar **{producto['nombre']}**?")
    st.warning("Esta acción borrará el producto del inventario permanentemente.")
    if st.button("SÍ, ELIMINAR DEFINITIVAMENTE", use_container_width=True):
        with st.spinner('Eliminando...'):
            supabase.table("productos").delete().eq("id", producto['id']).execute()
            time.sleep(1)
        st.success("✅ Eliminado correctamente.")
        time.sleep(0.5)
        st.rerun()

@st.dialog("⚠️ Confirmar Eliminación")
def modal_borrar_tecnico(nombre):
    st.write(f"¿Eliminar {nombre}?")
    if st.button("SÍ, ELIMINAR", use_container_width=True):
        with st.spinner('Eliminando...'):
            supabase.table("tecnicos").delete().eq("nombre", nombre).execute()
            time.sleep(1)
        st.success("✅ ¡Listo!")
        time.sleep(0.5)
        st.rerun()

@st.dialog("⚠️ Confirmar Eliminación")
def modal_borrar_local(nombre):
    st.write(f"¿Eliminar {nombre}?")
    if st.button("SÍ, ELIMINAR", use_container_width=True):
        with st.spinner('Eliminando...'):
            supabase.table("locales").delete().eq("nombre", nombre).execute()
            time.sleep(1)
        st.success("✅ ¡Listo!")
        time.sleep(0.5)
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
        busqueda = st.text_input("Buscar por modelo, marca o código...", placeholder="Ej: ip11 (para iPhone), Samsung, COD-123...")
    with col_b: 
        categoria = st.selectbox("Apartado", ["Todos", "⚠️ Solo Bajo Stock", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])

    items = supabase.table("productos").select("*").order("nombre").execute().data
    if items:
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

        # --- GRID SYSTEM ROBUSTO (FIX VISUAL DEFINITIVO) ---
        # Dividimos en grupos de 4 y dibujamos FILA POR FILA.
        # Esto mantiene el diseño de tarjetas pero evita que se rompa al filtrar.
        
        columnas_por_fila = 4
        chunks = [filtered_items[i:i + columnas_por_fila] for i in range(0, len(filtered_items), columnas_por_fila)]

        for chunk in chunks:
            cols = st.columns(columnas_por_fila)
            for i, p in enumerate(chunk):
                with cols[i]:
                    with st.container(border=True):
                        # Imagen protegida
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

                        # --- DISEÑO 3 COLUMNAS PARA PRECIOS (TU DISEÑO FAVORITO) ---
                        c1, c2, c3 = st.columns([1, 1.2, 1.2])
                        with c1: 
                            st.markdown(f"<div style='text-align:center; color:black; font-size:12px; font-weight:bold;'>Stock<br><span style='font-size:14px;'>{p['stock']}</span></div>", unsafe_allow_html=True)
                        with c2: 
                            st.markdown(f"<div style='text-align:center; color:#2c3e50; font-size:12px;'>Gral.<br><span style='font-weight:bold;'>S/ {p['precio_venta']}</span></div>", unsafe_allow_html=True)
                        with c3:
                            # Manejo seguro de precio punto
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
    c_title, c_btn = st.columns([3, 1])
    with c_title: st.markdown("<h2>📥 Añadir / Reponer Stock</h2>", unsafe_allow_html=True)
    with c_btn:
        if st.button("➕ NUEVO PRODUCTO", use_container_width=True): modal_nuevo_producto()
    
    all_products = supabase.table("productos").select("*").order("nombre").execute().data
    
    opciones_map = {}
    for p in all_products:
        marca = p.get('marca') or ""
        codigo = p.get('codigo_bateria')
        base_text = f"{marca} - {p['nombre']}" if marca else p['nombre']
        if codigo: display_text = f"{base_text} ({codigo})"
        else: display_text = base_text
        opciones_map[display_text] = p

    lista_opciones = sorted(list(opciones_map.keys()))
    
    st.write("Seleccione un producto existente para añadir stock o editarlo.")
    seleccion_str = st.selectbox("Modelo / Repuesto", ["Seleccionar"] + lista_opciones)
    
    if seleccion_str != "Seleccionar":
        prod_data = opciones_map[seleccion_str]
        if prod_data:
            with st.form("form_update_stock"):
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    st.text_input("Categoría", value=prod_data['categoria'], disabled=True)
                    
                    marca_val = prod_data.get('marca') or ""
                    new_marca = st.text_input("Marca", value=marca_val)
                    
                    cod_bat_new = ""
                    if prod_data['categoria'] == "Baterías":
                        current_code = prod_data.get('codigo_bateria') or ""
                        cod_bat_new = st.text_input("Código de Batería", value=current_code)

                with col_u2:
                    new_price_gen = st.number_input("Precio General (S/)", value=float(prod_data['precio_venta']), min_value=0.0, step=0.5)
                    
                    # Manejo seguro de posible null
                    val_actual_punto = float(prod_data.get('precio_punto') or 0.0)
                    new_price_punto = st.number_input("Precio Punto (S/)", value=val_actual_punto, min_value=0.0, step=0.5)
                    
                    img_val = prod_data.get('imagen_url') or ""
                    new_img = st.text_input("URL Imagen", value=img_val)

                st.divider()
                st.markdown(f"**Stock Actual:** {prod_data['stock']}")
                stock_add = st.number_input("Cantidad a AÑADIR (+)", min_value=0, value=0, step=1)
                
                if st.form_submit_button("CONSOLIDAR INGRESO"):
                    try:
                        with st.spinner('Guardando cambios...'):
                            total_stock = prod_data['stock'] + stock_add
                            datos_update = { 
                                "stock": total_stock, 
                                "precio_venta": new_price_gen, 
                                "precio_punto": new_price_punto,
                                "imagen_url": new_img,
                                "marca": new_marca 
                            }
                            if prod_data['categoria'] == "Baterías": datos_update["codigo_bateria"] = cod_bat_new

                            supabase.table("productos").update(datos_update).eq("id", prod_data['id']).execute()
                            
                            if stock_add > 0:
                                supabase.table("historial").insert({
                                    "producto_nombre": prod_data['nombre'], "cantidad": stock_add,
                                    "usuario": st.session_state.user, "tecnico": "Ingreso Stock", "local": "Almacén"
                                }).execute()
                            time.sleep(1)
                        st.success("✅ ¡Listo!")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al actualizar: {e}")
            
            st.markdown("---")
            if st.button("🗑️ ELIMINAR ESTE PRODUCTO DEL SISTEMA", type="primary"):
                modal_borrar_producto(prod_data)

elif opcion == "Log":
    st.markdown("<h2>📜 Historial General</h2>", unsafe_allow_html=True)
    col_d1, col_d2 = st.columns([1, 3])
    with col_d1:
        today = datetime.now()
        last_month = today - timedelta(days=30)
        date_range = st.date_input("Filtrar por Fecha", (last_month, today))
    
    logs = supabase.table("historial").select("*").order("fecha", desc=True).execute().data
    
    if logs:
        df = pd.DataFrame(logs)
        # --- FIX FECHAS (Para evitar TypeError) ---
        df['fecha_obj'] = pd.to_datetime(df['fecha'])
        df['fecha_date'] = df['fecha_obj'].dt.date
        
        if isinstance(date_range, tuple) and len(date_range) == 2:
            s_date = date_range[0]
            e_date = date_range[1]
            df = df[(df['fecha_date'] >= s_date) & (df['fecha_date'] <= e_date)]
            
        df['fecha'] = df['fecha_obj'].dt.strftime('%d/%m/%Y %H:%M')
        cols = ['fecha', 'producto_nombre', 'cantidad', 'usuario']
        if 'tecnico' in df.columns: cols.append('tecnico')
        if 'local' in df.columns: cols.append('local')
        st.dataframe(df[cols], use_container_width=True, hide_index=True)

elif opcion == "Stats":
    st.markdown("<h2>📊 Control y Estadísticas</h2>", unsafe_allow_html=True)
    date_range_stats = st.date_input("Rango de Análisis", (datetime.now() - timedelta(days=30), datetime.now()))

    productos_db = supabase.table("productos").select("*").execute().data
    historial_db = supabase.table("historial").select("*").execute().data
    
    if productos_db:
        df_prod = pd.DataFrame(productos_db)
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            total_unidades = df_prod['stock'].sum()
            st.metric("Total Unidades en Stock", f"{total_unidades}")
        with kpi2:
            valor_inventario = (df_prod['stock'] * df_prod['precio_venta']).sum()
            st.metric("Valor del Inventario", f"S/ {valor_inventario:,.2f}")
        with kpi3:
            st.metric("Total Referencias", f"{len(df_prod)}")
        
        st.divider()

        if historial_db:
            df_hist = pd.DataFrame(historial_db)
            df_hist['fecha_obj'] = pd.to_datetime(df_hist['fecha'])
            df_hist['fecha_date'] = df_hist['fecha_obj'].dt.date
            
            if isinstance(date_range_stats, tuple) and len(date_range_stats) == 2:
                s_date = date_range_stats[0]
                e_date = date_range_stats[1]
                df_hist = df_hist[(df_hist['fecha_date'] >= s_date) & (df_hist['fecha_date'] <= e_date)]
            
            df_salidas = df_hist[df_hist['cantidad'] < 0].copy()
            df_salidas['cantidad'] = df_salidas['cantidad'].abs()
            
            df_merged = df_salidas.merge(df_prod, left_on='producto_nombre', right_on='nombre', how='left')
            
            c1, c2 = st.columns([1, 1])
            with c1:
                st.subheader("Top 10 Productos Más Usados")
                if not df_salidas.empty:
                    top_gen = df_salidas.groupby('producto_nombre')['cantidad'].sum().reset_index().sort_values('cantidad', ascending=False).head(10)
                    fig_top = px.bar(top_gen, x='cantidad', y='producto_nombre', orientation='h', text='cantidad')
                    st.plotly_chart(fig_top, use_container_width=True)
                else:
                    st.info("No hay movimientos en este rango de fechas.")
            
            with c2:
                st.subheader("Análisis por Categoría")
                cats_disponibles = ["Pantallas", "Baterías", "Flex", "Glases", "Otros"]
                cat_filter = st.selectbox("Selecciona Categoría:", cats_disponibles)
                
                if not df_merged.empty:
                    df_cat_specific = df_merged[df_merged['categoria'] == cat_filter]
                    if not df_cat_specific.empty:
                        top_cat = df_cat_specific.groupby('producto_nombre')['cantidad'].sum().reset_index().sort_values('cantidad', ascending=False)
                        fig_cat = px.bar(top_cat, x='producto_nombre', y='cantidad', text='cantidad', 
                                         color='cantidad', color_continuous_scale='Blues')
                        st.plotly_chart(fig_cat, use_container_width=True)
                    else:
                        st.info(f"Sin movimientos de {cat_filter} en estas fechas.")

elif opcion == "Users":
    st.markdown("<h2>👥 Gestión</h2>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🔑 Accesos", "👨‍🔧 Técnicos", "🏠 Locales"])
    with tab1:
        with st.form("nu"):
            un = st.text_input("Usuario")
            pw = st.text_input("Clave")
            rl = st.selectbox("Rol", ["Normal", "Super"])
            if st.form_submit_button("CREAR"):
                if supabase.table("usuarios").select("*").eq("usuario", un).execute().data: st.error("Existe.")
                else:
                    with st.spinner('Creando usuario...'):
                        supabase.table("usuarios").insert({"usuario":un, "contrasena":pw, "rol":rl}).execute()
                        time.sleep(1)
                    st.success("✅ ¡Listo!")
                    time.sleep(0.5)
    with tab2:
        with st.form("nt"):
            tn = st.text_input("Nombre")
            if st.form_submit_button("AGREGAR"):
                with st.spinner('Guardando...'):
                    supabase.table("tecnicos").insert({"nombre": tn}).execute()
                    time.sleep(1)
                st.success("✅ ¡Listo!")
                time.sleep(0.5)
                st.rerun()
        st.write("---")
        tecs = supabase.table("tecnicos").select("*").execute().data
        if tecs:
            col_a, col_b = st.columns([3,1])
            with col_a: t_del = st.selectbox("Borrar Técnico", [t['nombre'] for t in tecs])
            with col_b: 
                st.write("")
                st.write("")
                if st.button("🗑️", key="bt"): modal_borrar_tecnico(t_del)
            st.dataframe(pd.DataFrame(tecs), use_container_width=True)
    with tab3:
        with st.form("nl"):
            ln = st.text_input("Nombre")
            if st.form_submit_button("AGREGAR"):
                with st.spinner('Guardando...'):
                    supabase.table("locales").insert({"nombre": ln}).execute()
                    time.sleep(1)
                st.success("✅ ¡Listo!")
                time.sleep(0.5)
                st.rerun()
        st.write("---")
        locs = supabase.table("locales").select("*").execute().data
        if locs:
            col_a, col_b = st.columns([3,1])
            with col_a: l_del = st.selectbox("Borrar Local", [l['nombre'] for l in locs])
            with col_b:
                st.write("")
                st.write("") 
                if st.button("🗑️", key="bl"): modal_borrar_local(l_del)
            st.dataframe(pd.DataFrame(locs), use_container_width=True)

elif opcion == "Prov":
    st.markdown("<h2>📞 Proveedores</h2>", unsafe_allow_html=True)
    provs = supabase.table("proveedores").select("*").execute().data
    if provs:
        for pr in provs:
            with st.container(border=True):
                st.markdown(f"**{pr['nombre_contacto']}**")
                st.link_button("WhatsApp", f"https://wa.me/{pr['whatsapp']}")
