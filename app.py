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

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align:center; color:#2488bc;'>VILLAFIX ACCESS</h1>", unsafe_allow_html=True)
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

# --- CSS MAESTRO (VISIBILIDAD, MODALES Y DISEÑO) ---
st.markdown("""
    <style>
    /* 1. FONDO BLANCO GLOBAL */
    .stApp, .main, .block-container {
        background-color: #ffffff !important;
    }

    /* 2. BARRA LATERAL (OSCURA) */
    [data-testid="stSidebar"] {
        background-color: #1a222b !important;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    [data-testid="stSidebar"] button {
        background-color: transparent !important;
        border: none !important;
        color: #bdc3c7 !important;
        text-align: left !important;
        padding-left: 15px !important;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: rgba(255,255,255,0.05) !important;
        border-left: 4px solid #3498db !important;
        color: #ffffff !important;
    }

    /* 3. TEXTOS NEGROS OBLIGATORIOS */
    div[data-testid="stWidgetLabel"] p, label, .stMarkdown p, h1, h2, h3, .stDialog p, .stDialog label, div[role="dialog"] p, .stMetriclabel {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 700 !important;
    }
    
    /* Metrics (KPIs) */
    div[data-testid="stMetricValue"] {
        color: #2488bc !important;
        -webkit-text-fill-color: #2488bc !important;
    }

    /* 4. CAJAS DE TEXTO (INPUTS) */
    input, textarea, .stNumberInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border: 1px solid #888888 !important;
        caret-color: #000000 !important;
    }
    input:disabled {
        background-color: #e9ecef !important;
        color: #555555 !important;
        -webkit-text-fill-color: #555555 !important;
    }
    ::placeholder {
        color: #666666 !important;
        -webkit-text-fill-color: #666666 !important;
        opacity: 1 !important;
    }

    /* 5. MENÚS DESPLEGABLES */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #888888 !important;
    }
    div[data-baseweb="select"] span { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important;
    }
    ul[data-testid="stSelectboxVirtualDropdown"] {
        background-color: #ffffff !important;
    }
    ul[data-testid="stSelectboxVirtualDropdown"] li {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    ul[data-testid="stSelectboxVirtualDropdown"] li:hover {
        background-color: #f0f2f6 !important;
    }

    /* 6. VENTANAS FLOTANTES */
    div[role="dialog"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* 7. TARJETAS DE STOCK (ALINEACIÓN) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 1px solid #ddd !important;
        padding: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        height: 100% !important; 
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    div[data-testid="stImage"] {
        display: flex !important;
        justify-content: center !important; 
        align-items: center !important;
        width: 100% !important;
        margin: 0 auto !important;
        height: 160px !important; 
    }
    div[data-testid="stImage"] img {
        display: block !important;
        margin-left: auto !important;
        margin-right: auto !important;
        max-height: 150px !important;
        width: auto !important;
        object-fit: contain !important;
    }

    /* 8. BOTONES */
    div.stButton button {
        background-color: #2488bc !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: bold !important;
        width: 100% !important;
        margin-top: auto !important;
    }
    div.stButton button p { color: #ffffff !important; }

    /* Botón NO STOCK (ROJO) */
    div.stButton button:disabled, button[kind="secondary"] {
        background-color: #e74c3c !important;
        color: white !important;
        opacity: 1 !important;
        border: 1px solid #c0392b !important;
    }
    div.stButton button:disabled p { color: white !important; }
    
    /* Pestañas */
    button[data-baseweb="tab"] { color: #000000 !important; }
    div[data-baseweb="tab-list"] { background-color: #f1f3f4 !important; border-radius: 8px; }

    /* Perfil */
    .profile-section { text-align: center !important; padding: 20px 0px; }
    .profile-pic { width: 100px; height: 100px; border-radius: 50%; border: 3px solid #f39c12; object-fit: cover; display: block; margin: 0 auto 10px auto; }

    [data-testid="stSidebarNav"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# --- VENTANAS FLOTANTES ---

@st.dialog("Registrar Salida")
def modal_salida(producto):
    st.markdown(f"<h3 style='color:black;'>{producto['nombre']}</h3>", unsafe_allow_html=True)
    st.markdown(f"**Stock:** {producto['stock']}")
    
    try: techs = [t['nombre'] for t in supabase.table("tecnicos").select("nombre").execute().data]
    except: techs = ["General"]
    try: locs = [l['nombre'] for l in supabase.table("locales").select("nombre").execute().data]
    except: locs = ["Principal"]

    with st.form("form_salida_modal"):
        tecnico = st.selectbox("Técnico", ["Seleccionar"] + techs)
        local = st.selectbox("Local", ["Seleccionar"] + locs)
        cantidad = st.number_input("Cantidad", min_value=1, max_value=producto['stock'], step=1)
        if st.form_submit_button("CONFIRMAR SALIDA"):
            if tecnico == "Seleccionar" or local == "Seleccionar":
                st.error("⚠️ Faltan datos.")
            else:
                nuevo_stock = producto['stock'] - cantidad
                supabase.table("productos").update({"stock": nuevo_stock}).eq("id", producto['id']).execute()
                supabase.table("historial").insert({
                    "producto_nombre": producto['nombre'], "cantidad": -cantidad,
                    "usuario": st.session_state.user, "tecnico": tecnico, "local": local
                }).execute()
                st.success("Listo.")
                st.rerun()

@st.dialog("✨ Nuevo Producto")
def modal_nuevo_producto():
    st.markdown("<h3 style='color:black;'>Crear Producto</h3>", unsafe_allow_html=True)
    with st.form("form_nuevo_prod"):
        n = st.text_input("Nombre / Modelo *")
        c = st.selectbox("Categoría *", ["Seleccionar", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])
        m = st.text_input("Marca (Solo si aplica)")
        cb = st.text_input("Código de Batería (Solo para Baterías)")
        s = st.number_input("Stock Inicial *", min_value=0, step=1)
        p = st.number_input("Precio Venta (S/) *", min_value=0.0, step=0.5)
        img = st.text_input("URL Imagen (Opcional)")

        if st.form_submit_button("GUARDAR"):
            if not n or c == "Seleccionar" or p <= 0:
                st.error("⚠️ Datos incompletos.")
            else:
                existe = supabase.table("productos").select("*").eq("nombre", n).execute()
                if existe.data:
                    st.error("⚠️ Ya existe.")
                else:
                    supabase.table("productos").insert({
                        "nombre": n, 
                        "categoria": c, 
                        "marca": m, 
                        "codigo_bateria": cb,
                        "stock": s, 
                        "precio_venta": p, 
                        "imagen_url": img
                    }).execute()
                    
                    supabase.table("historial").insert({
                        "producto_nombre": n, "cantidad": s, "usuario": st.session_state.user,
                        "tecnico": "Ingreso Inicial", "local": "Almacén"
                    }).execute()
                    st.success("Creado.")
                    st.rerun()

@st.dialog("⚠️ Confirmar")
def modal_borrar_tecnico(nombre):
    st.write(f"¿Eliminar {nombre}?")
    if st.button("SÍ, ELIMINAR", use_container_width=True):
        supabase.table("tecnicos").delete().eq("nombre", nombre).execute()
        st.success("Hecho.")
        st.rerun()

@st.dialog("⚠️ Confirmar")
def modal_borrar_local(nombre):
    st.write(f"¿Eliminar {nombre}?")
    if st.button("SÍ, ELIMINAR", use_container_width=True):
        supabase.table("locales").delete().eq("nombre", nombre).execute()
        st.success("Hecho.")
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
        if st.button("⚙️ Reset Sistema", use_container_width=True): st.session_state.menu = "Reset"

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# --- ÁREA CENTRAL ---
opcion = st.session_state.menu

if opcion == "Stock":
    st.markdown("<h2>Inventario General</h2>", unsafe_allow_html=True)
    col_a, col_b = st.columns([3, 1])
    with col_a: busqueda = st.text_input("Buscar por modelo", placeholder="Ej: Pantalla iPhone...")
    with col_b: categoria = st.selectbox("Apartado", ["Todos", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])

    items = supabase.table("productos").select("*").order("nombre").execute().data
    if items:
        # Filtrado
        filtered_items = []
        busqueda_lower = busqueda.lower()
        for p in items:
            nombre_prod = p['nombre'].lower()
            marca_prod = (p.get('marca') or '').lower()
            codigo_prod = (p.get('codigo_bateria') or '').lower()
            
            match_busqueda = (busqueda_lower in nombre_prod) or \
                             (busqueda_lower in marca_prod) or \
                             (busqueda_lower in codigo_prod)
            
            match_categoria = (categoria == "Todos" or p['categoria'] == categoria)
            if match_busqueda and match_categoria:
                filtered_items.append(p)
        
        # Ordenamiento
        if busqueda_lower:
            filtered_items.sort(key=lambda x: 0 if x['nombre'].lower().startswith(busqueda_lower) else 1)

        cols = st.columns(4)
        for i, p in enumerate(filtered_items):
            with cols[i % 4]:
                with st.container(border=True):
                    # Imagen
                    img_url = p.get('imagen_url') or "https://via.placeholder.com/150"
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

                    c1, c2 = st.columns(2)
                    with c1: st.markdown(f"<div style='text-align:center; color:black; font-size:13px;'>U: {p['stock']}</div>", unsafe_allow_html=True)
                    with c2: st.markdown(f"<div style='text-align:center; color:black; font-size:13px;'>S/ {p['precio_venta']}</div>", unsafe_allow_html=True)
                    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                    
                    if p['stock'] > 0:
                        if st.button("SALIDA", key=f"s_{p['id']}", use_container_width=True): modal_salida(p)
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
    seleccion_str = st.selectbox("Modelo / Repuesto (Busca por Marca, Modelo o Código)", ["Seleccionar"] + lista_opciones)
    
    if seleccion_str != "Seleccionar":
        prod_data = opciones_map[seleccion_str]
        if prod_data:
            with st.form("form_update_stock"):
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    st.text_input("Categoría", value=prod_data['categoria'], disabled=True)
                    marca_val = prod_data.get('marca') or ""
                    st.text_input("Marca", value=marca_val, disabled=True)
                    
                    cod_bat_new = ""
                    if prod_data['categoria'] == "Baterías":
                        current_code = prod_data.get('codigo_bateria') or ""
                        cod_bat_new = st.text_input("Código de Batería", value=current_code)

                with col_u2:
                    new_price = st.number_input("Precio Venta (S/)", value=float(prod_data['precio_venta']), min_value=0.0, step=0.5)
                    img_val = prod_data.get('imagen_url') or ""
                    new_img = st.text_input("URL Imagen", value=img_val)

                st.divider()
                st.markdown(f"**Stock Actual:** {prod_data['stock']}")
                stock_add = st.number_input("Cantidad a AÑADIR (+)", min_value=0, value=0, step=1)
                
                if st.form_submit_button("CONSOLIDAR INGRESO"):
                    total_stock = prod_data['stock'] + stock_add
                    datos_update = { "stock": total_stock, "precio_venta": new_price, "imagen_url": new_img }
                    if prod_data['categoria'] == "Baterías": datos_update["codigo_bateria"] = cod_bat_new

                    supabase.table("productos").update(datos_update).eq("id", prod_data['id']).execute()
                    
                    if stock_add > 0:
                        supabase.table("historial").insert({
                            "producto_nombre": prod_data['nombre'], "cantidad": stock_add,
                            "usuario": st.session_state.user, "tecnico": "Ingreso Stock", "local": "Almacén"
                        }).execute()
                    st.success("Actualizado.")
                    st.rerun()

elif opcion == "Log":
    st.markdown("<h2>📜 Historial</h2>", unsafe_allow_html=True)
    logs = supabase.table("historial").select("*").order("fecha", desc=True).execute().data
    if logs:
        df = pd.DataFrame(logs)
        df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m/%Y %H:%M')
        cols = ['fecha', 'producto_nombre', 'cantidad', 'usuario']
        if 'tecnico' in df.columns: cols.append('tecnico')
        if 'local' in df.columns: cols.append('local')
        st.dataframe(df[cols], use_container_width=True, hide_index=True)

# --- SECCIÓN ESTADÍSTICAS MEJORADA ---
elif opcion == "Stats":
    st.markdown("<h2>📊 Control y Estadísticas</h2>", unsafe_allow_html=True)
    
    # 1. Recuperar Datos
    productos_db = supabase.table("productos").select("*").execute().data
    historial_db = supabase.table("historial").select("*").execute().data
    
    if productos_db:
        df_prod = pd.DataFrame(productos_db)
        
        # --- KPIS PRINCIPALES ---
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

        # 2. PROCESAMIENTO DE SALIDAS (HISTORIAL)
        if historial_db:
            df_hist = pd.DataFrame(historial_db)
            # Filtramos solo salidas (cantidad negativa)
            df_salidas = df_hist[df_hist['cantidad'] < 0].copy()
            df_salidas['cantidad'] = df_salidas['cantidad'].abs() # Convertir a positivo para graficar
            
            # Unimos historial con productos para saber la categoría de lo que se vendió
            # (Usamos el nombre como llave, ya que historial guarda nombre)
            df_merged = df_salidas.merge(df_prod, left_on='producto_nombre', right_on='nombre', how='left')
            
            # --- FILA 1: GENERAL ---
            c1, c2 = st.columns([1, 1])
            
            with c1:
                st.subheader("Stock Actual por Categoría")
                fig_stock = px.pie(df_prod, names='categoria', values='stock', hole=0.4)
                st.plotly_chart(fig_stock, use_container_width=True)
            
            with c2:
                st.subheader("Top 10 Productos Más Usados (General)")
                if not df_salidas.empty:
                    top_gen = df_salidas.groupby('producto_nombre')['cantidad'].sum().reset_index().sort_values('cantidad', ascending=False).head(10)
                    fig_top = px.bar(top_gen, x='cantidad', y='producto_nombre', orientation='h', text='cantidad')
                    st.plotly_chart(fig_top, use_container_width=True)
                else:
                    st.info("No hay datos de salidas aún.")

            st.divider()
            
            # --- FILA 2: DETALLE POR CATEGORÍA (TU PEDIDO) ---
            st.markdown("### 🔎 Análisis Detallado: ¿Qué modelos se mueven más?")
            
            # Selector de Categoría
            cats_disponibles = ["Pantallas", "Baterías", "Flex", "Glases", "Otros"]
            cat_filter = st.selectbox("Selecciona una Categoría para ver sus movimientos:", cats_disponibles)
            
            if not df_merged.empty:
                # Filtrar por la categoría seleccionada
                df_cat_specific = df_merged[df_merged['categoria'] == cat_filter]
                
                if not df_cat_specific.empty:
                    # Agrupar por nombre de producto y sumar cantidad
                    top_cat = df_cat_specific.groupby('producto_nombre')['cantidad'].sum().reset_index().sort_values('cantidad', ascending=False)
                    
                    st.write(f"Ranking de modelos usados en **{cat_filter}**:")
                    fig_cat = px.bar(top_cat, x='producto_nombre', y='cantidad', text='cantidad', 
                                     color='cantidad', color_continuous_scale='Blues')
                    st.plotly_chart(fig_cat, use_container_width=True)
                else:
                    st.warning(f"No se han registrado salidas en la categoría {cat_filter} todavía.")
            else:
                st.info("Registra salidas para ver estadísticas detalladas.")

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
                    supabase.table("usuarios").insert({"usuario":un, "contrasena":pw, "rol":rl}).execute()
                    st.success("Creado.")
    with tab2:
        with st.form("nt"):
            tn = st.text_input("Nombre")
            if st.form_submit_button("AGREGAR"):
                supabase.table("tecnicos").insert({"nombre": tn}).execute()
                st.success("Hecho.")
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
                supabase.table("locales").insert({"nombre": ln}).execute()
                st.success("Hecho.")
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

elif opcion == "Reset":
    st.markdown("<h2>⚙️ Reset</h2>", unsafe_allow_html=True)
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("BORRAR STOCK TOTAL", use_container_width=True):
            data = supabase.table("productos").select("id").execute().data
            for item in data: supabase.table("productos").delete().eq("id", item['id']).execute()
            st.success("Hecho.")
    with col_r2:
        if st.button("BORRAR HISTORIAL TOTAL", use_container_width=True):
            data = supabase.table("historial").select("id").execute().data
            for item in data: supabase.table("historial").delete().eq("id", item['id']).execute()
            st.success("Hecho.")
