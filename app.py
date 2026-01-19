import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, date
import time

# ==============================================================================
# 1. CONFIGURACIÓN: BARRA SIEMPRE ABIERTA (OBLIGATORIO)
# ==============================================================================
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except:
    st.error("⚠️ Error crítico de conexión. Verifica tus 'secrets' en Streamlit.")
    st.stop()

# 'initial_sidebar_state="expanded"' OBLIGA a que la barra arranque abierta
st.set_page_config(page_title="VillaFix | Admin", page_icon="🛠️", layout="wide", initial_sidebar_state="expanded")

# ==============================================================================
# 2. CSS NUCLEAR: ELIMINAR FLECHAS << Y FIJAR BARRA
# ==============================================================================
st.markdown("""
    <style>
    /* ============================================================
       1. ZONA CRÍTICA: BORRAR EL BOTÓN DE CERRAR BARRA (<<)
       ============================================================ */
    
    /* Selector específico para el botón de colapsar dentro del Sidebar */
    section[data-testid="stSidebar"] button[kind="header"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Selector global para el control de colapso */
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Ajuste para que no quede un hueco vacío arriba en la barra */
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1rem !important;
    }

    /* ============================================================
       2. OCULTAR BARRA SUPERIOR, DECORACIONES Y MANAGE APP
       ============================================================ */
    [data-testid="stToolbar"] {
        visibility: hidden !important;
        display: none !important;
    }
    header {
        background-color: transparent !important;
    }
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    /* Ocultar pie de página */
    footer {
        display: none !important;
        height: 0px !important;
    }
    
    /* ============================================================
       3. ESTILOS DE LA APP (DISEÑO LIMPIO)
       ============================================================ */
    .stApp, .main, .block-container { background-color: #ffffff !important; }
    
    /* Sidebar (Color Oscuro) */
    [data-testid="stSidebar"] { background-color: #1a222b !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
    
    /* Estilo de los botones del menú lateral (Tus botones personalizados) */
    [data-testid="stSidebar"] button { 
        background-color: transparent !important; 
        border: none !important; 
        color: #bdc3c7 !important; 
        text-align: left !important; 
        padding-left: 15px !important; 
        transition: 0.3s; 
    }
    /* Efecto Hover en menú */
    [data-testid="stSidebar"] button:hover { 
        background-color: rgba(255,255,255,0.05) !important; 
        border-left: 4px solid #3498db !important; 
        color: #ffffff !important; 
        padding-left: 25px !important; 
    }
    
    /* Textos Generales (Negro) */
    div[data-testid="stWidgetLabel"] p, label, h1, h2, h3, .stDialog p, .stDialog label, div[role="dialog"] p, .stMetricLabel { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
        font-weight: 700 !important; 
    }
    div[data-testid="stMetricValue"] { color: #2488bc !important; -webkit-text-fill-color: #2488bc !important; }
    
    /* Inputs */
    input, textarea, .stNumberInput input { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
        border: 1px solid #888888 !important; 
    }
    input:disabled { 
        background-color: #e9ecef !important; 
        color: #555555 !important; 
        -webkit-text-fill-color: #555555 !important; 
    }
    
    /* Tarjetas y Elementos UI */
    div[role="dialog"] { background-color: #ffffff !important; color: #000000 !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { 
        background-color: #ffffff !important; 
        border: 1px solid #ddd !important; 
        padding: 10px !important; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important; 
        display: flex; flex-direction: column; justify-content: space-between; 
    }
    div[data-testid="stImage"] { display: flex !important; justify-content: center !important; height: 160px !important; }
    div[data-testid="stImage"] img { max-height: 150px !important; width: auto !important; object-fit: contain !important; }
    
    /* Botones de acción */
    div.stButton button { background-color: #2488bc !important; color: #ffffff !important; border: none !important; font-weight: bold !important; width: 100% !important; margin-top: auto !important; }
    div.stButton button p { color: #ffffff !important; }
    div.stButton button:disabled, button[kind="secondary"] { background-color: #e74c3c !important; color: white !important; opacity: 1 !important; border: 1px solid #c0392b !important; }
    div.stButton button:disabled p { color: white !important; }
    
    /* Perfil */
    .profile-section { text-align: center !important; padding: 20px 0px; }
    .profile-pic { width: 100px; height: 100px; border-radius: 50%; border: 3px solid #f39c12; object-fit: cover; display: block; margin: 0 auto 10px auto; }
    [data-testid="stSidebarNav"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. SISTEMA DE SESIÓN (12 HORAS)
# ==============================================================================
SESSION_DURATION = 12 * 3600 

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.rol = None
    st.session_state.user = None
    st.session_state.menu = "Stock"
    st.session_state.login_time = 0

if not st.session_state.autenticado:
    params = st.query_params
    if "user_session" in params:
        user_in_url = params["user_session"]
        try:
            res = supabase.table("usuarios").select("*").eq("usuario", user_in_url).execute()
            if res.data:
                st.session_state.autenticado = True
                st.session_state.user = user_in_url
                st.session_state.rol = res.data[0]['rol']
                st.session_state.login_time = time.time()
                st.rerun()
        except:
            pass

if st.session_state.autenticado:
    if (time.time() - st.session_state.login_time) > SESSION_DURATION:
        st.session_state.autenticado = False
        st.query_params.clear()
        st.rerun()

# --- LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<br><br><h1 style='text-align:center; color:#2488bc;'>VILLAFIX SYSTEM</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        with st.container(border=True):
            st.markdown("<h3 style='text-align:center;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
            with st.form("login_form"):
                u = st.text_input("Usuario")
                p = st.text_input("Contraseña", type="password")
                submit = st.form_submit_button("INGRESAR", use_container_width=True)
            
            if submit:
                try:
                    res = supabase.table("usuarios").select("*").eq("usuario", u).eq("contrasena", p).execute()
                    if res.data:
                        st.session_state.autenticado = True
                        st.session_state.rol = res.data[0]['rol']
                        st.session_state.user = u
                        st.session_state.login_time = time.time()
                        st.query_params["user_session"] = u
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas")
                except:
                    st.error("Error de conexión")
    st.stop()

# ==============================================================================
# 4. FUNCIONES
# ==============================================================================
def es_coincidencia(busqueda, texto_db):
    if not busqueda: return True 
    if not texto_db: return False
    b = str(busqueda).lower().strip()
    if b.startswith("ip") and len(b) > 2 and b[2].isdigit(): b = b.replace("ip", "iphone", 1)
    elif b == "ip": b = "iphone"
    b_nospace = b.replace(" ", "").replace("-", "")
    t = str(texto_db).lower()
    t_nospace = t.replace(" ", "").replace("-", "")
    if b in t: return True
    if b_nospace in t_nospace: return True
    return False

# ==============================================================================
# 5. MODALES
# ==============================================================================
@st.dialog("Gestionar Inventario")
def modal_gestion(producto):
    st.markdown(f"<h3 style='color:black;'>{producto['nombre']}</h3>", unsafe_allow_html=True)
    tab_salida, tab_devolucion = st.tabs(["📉 SALIDA", "↩️ DEVOLUCIÓN"])
    
    with tab_salida:
        st.markdown(f"**Stock Actual:** {producto['stock']}")
        try: techs = [t['nombre'] for t in supabase.table("tecnicos").select("nombre").execute().data]
        except: techs = ["General"]
        try: locs = [l['nombre'] for l in supabase.table("locales").select("nombre").execute().data]
        except: locs = ["Principal"]

        # Sin st.form
        tecnico = st.selectbox("Técnico", ["Seleccionar"] + techs, key="ts")
        local = st.selectbox("Local", ["Seleccionar"] + locs, key="ls")
        max_val = producto['stock'] if producto['stock'] > 0 else 1
        cantidad = st.number_input("Cantidad a RETIRAR", min_value=1, max_value=max_val, step=1, key="cs")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("CONFIRMAR SALIDA", use_container_width=True):
            if producto['stock'] <= 0: st.error("⚠️ Sin stock.")
            elif tecnico == "Seleccionar" or local == "Seleccionar": st.error("⚠️ Faltan datos.")
            else:
                with st.spinner('Procesando...'):
                    supabase.table("productos").update({"stock": producto['stock'] - cantidad}).eq("id", producto['id']).execute()
                    supabase.table("historial").insert({"producto_nombre": producto['nombre'], "cantidad": -cantidad, "usuario": st.session_state.user, "tecnico": tecnico, "local": local}).execute()
                    time.sleep(0.5)
                st.success("✅ Listo")
                time.sleep(0.5)
                st.rerun()

    with tab_devolucion:
        razon = st.text_input("Motivo", "Devolución")
        cant_dev = st.number_input("Cantidad", 1, step=1, key="cd")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("INGRESAR", use_container_width=True):
            with st.spinner('Procesando...'):
                supabase.table("productos").update({"stock": producto['stock'] + cant_dev}).eq("id", producto['id']).execute()
                supabase.table("historial").insert({"producto_nombre": producto['nombre'], "cantidad": cant_dev, "usuario": st.session_state.user, "tecnico": razon, "local": "Almacén"}).execute()
                time.sleep(0.5)
            st.success("✅ Listo")
            time.sleep(0.5)
            st.rerun()

@st.dialog("✨ Nuevo Producto")
def modal_nuevo_producto():
    st.markdown("<h3 style='color:black;'>Crear Producto</h3>", unsafe_allow_html=True)
    n = st.text_input("Nombre / Modelo *")
    c1, c2 = st.columns(2)
    with c1: cat = st.selectbox("Categoría *", ["Pantallas", "Baterías", "Flex", "Glases", "Otros"])
    with c2: m = st.text_input("Marca")
    cod = st.text_input("Código de Batería")
    s = st.number_input("Stock Inicial", 0)
    p1, p2 = st.columns(2)
    with p1: pg = st.number_input("Precio Gral", 0.0)
    with p2: pp = st.number_input("Precio Punto", 0.0)
    img = st.text_input("URL Imagen")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("GUARDAR PRODUCTO", type="primary", use_container_width=True):
        if not n or pg <= 0: st.error("⚠️ Faltan datos.")
        else:
            q = supabase.table("productos").select("id").eq("nombre", n).eq("marca", m).eq("categoria", cat)
            if cod: q = q.eq("codigo_bateria", cod)
            else: q = q.eq("codigo_bateria", "")
            if q.execute().data: st.error("⚠️ Producto Duplicado.")
            else:
                with st.spinner('Guardando...'):
                    supabase.table("productos").insert({"nombre": n, "categoria": cat, "marca": m, "codigo_bateria": cod, "stock": s, "precio_venta": pg, "precio_punto": pp, "imagen_url": img}).execute()
                    supabase.table("historial").insert({"producto_nombre": n, "cantidad": s, "usuario": st.session_state.user, "tecnico": "Inicio", "local": "Almacén"}).execute()
                    time.sleep(1)
                st.success("✅ Creado")
                time.sleep(0.5)
                st.rerun()

@st.dialog("⚠️ Eliminar")
def modal_borrar(p):
    st.write(f"¿Borrar {p['nombre']}?")
    if st.button("SÍ, BORRAR DEFINITIVAMENTE", type="primary", use_container_width=True):
        supabase.table("productos").delete().eq("id", p['id']).execute()
        st.success("✅ Borrado")
        time.sleep(0.5)
        st.rerun()

@st.dialog("⚠️ Borrar Técnico")
def modal_borrar_tecnico(nombre):
    st.write(f"¿Eliminar a {nombre}?")
    if st.button("SÍ", use_container_width=True):
        supabase.table("tecnicos").delete().eq("nombre", nombre).execute()
        st.rerun()

@st.dialog("⚠️ Borrar Local")
def modal_borrar_local(nombre):
    st.write(f"¿Eliminar {nombre}?")
    if st.button("SÍ", use_container_width=True):
        supabase.table("locales").delete().eq("nombre", nombre).execute()
        st.rerun()

# ==============================================================================
# 6. SIDEBAR (FIJO)
# ==============================================================================
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
        st.query_params.clear()
        st.rerun()

# ==============================================================================
# 7. VISTAS PRINCIPALES
# ==============================================================================
opcion = st.session_state.menu

if opcion == "Stock":
    st.markdown("<h2>Inventario General</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1: bus = st.text_input("Buscar...", placeholder="Modelo, Marca, Código...")
    with c2: cat = st.selectbox("Filtro", ["Todos", "⚠️ Solo Bajo Stock", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])
    
    data = supabase.table("productos").select("*").order("nombre").execute().data
    if data:
        filtro = []
        for p in data:
            match = es_coincidencia(bus, p['nombre']) or es_coincidencia(bus, p.get('marca')) or es_coincidencia(bus, p.get('codigo_bateria'))
            if cat == "⚠️ Solo Bajo Stock" and p['stock'] <= 2 and match: filtro.append(p)
            elif cat != "Todos" and p['categoria'] == cat and match: filtro.append(p)
            elif cat == "Todos" and match: filtro.append(p)
        
        N_COLS = 4
        rows = [filtro[i:i + N_COLS] for i in range(0, len(filtro), N_COLS)]
        for row in rows:
            cols = st.columns(N_COLS)
            for i, p in enumerate(row):
                with cols[i]:
                    with st.container(border=True):
                        u_img = p.get('imagen_url') if p.get('imagen_url') else "https://via.placeholder.com/150"
                        st.markdown(f"""
                            <div style="display: flex; justify-content: center; align-items: center; height: 160px; width: 100%; margin-bottom: 10px;">
                                <img src="{u_img}" style="max-height: 150px; width: auto; object-fit: contain;">
                            </div>
                        """, unsafe_allow_html=True)
                        marca = p.get('marca', '')
                        cod = p.get('codigo_bateria', '')
                        st.markdown(f"""
                            <div style="text-align:center; height:90px; display:flex; flex-direction:column; justify-content:flex-start; align-items:center;">
                                <div style='color:#555; font-size:11px; font-weight:bold; text-transform:uppercase;'>{marca}</div>
                                <div style="color:black; font-weight:bold; font-size:15px; line-height:1.2; margin-top:2px;">{p['nombre']}</div>
                                <div style='color:#555; font-size:11px; font-weight:bold; text-transform:uppercase; margin-top:2px;'>{cod}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        k1, k2, k3 = st.columns([1, 1.2, 1.2])
                        with k1: st.markdown(f"<div style='text-align:center; color:black; font-size:12px; font-weight:bold;'>Stock<br><span style='font-size:14px;'>{p['stock']}</span></div>", unsafe_allow_html=True)
                        with k2: st.markdown(f"<div style='text-align:center; color:#2c3e50; font-size:12px;'>Gral.<br><span style='font-weight:bold;'>S/ {p['precio_venta']}</span></div>", unsafe_allow_html=True)
                        with k3: 
                            pp = p.get('precio_punto', 0)
                            col_p = "#27ae60" if pp else "#bdc3c7"
                            val_p = f"S/ {pp}" if pp else "--"
                            st.markdown(f"<div style='text-align:center; color:{col_p}; font-size:12px;'>Punto<br><span style='font-weight:bold;'>{val_p}</span></div>", unsafe_allow_html=True)
                        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                        if p['stock'] > 0: 
                            if st.button("SALIDA", key=f"s{p['id']}", use_container_width=True): modal_gestion(p)
                        else: st.button("🚫 NO STOCK", disabled=True, key=f"n{p['id']}", use_container_width=True)

elif opcion == "Carga":
    c_title, c_btn = st.columns([3, 1])
    with c_title: st.markdown("<h2>📥 Añadir / Reponer Stock</h2>", unsafe_allow_html=True)
    with c_btn:
        if st.button("➕ NUEVO PRODUCTO", use_container_width=True): modal_nuevo_producto()
    
    prods = supabase.table("productos").select("*").order("nombre").execute().data
    mapa = {}
    for p in prods:
        nom = f"{p['nombre']}"
        if p.get('marca'): nom = f"{p['marca']} - {nom}"
        if p.get('codigo_bateria'): nom += f" ({p['codigo_bateria']})"
        mapa[nom] = p
    
    lista = sorted(list(mapa.keys()))
    sel = st.selectbox("Seleccione Producto para Editar:", ["Seleccionar"] + lista)
    
    if sel != "Seleccionar":
        p = mapa[sel]
        with st.container(border=True):
            st.markdown(f"### Editando: {p['nombre']}")
            
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Categoría (Bloqueado)", p['categoria'], disabled=True)
                st.text_input("Marca (Bloqueado)", p.get('marca',''), disabled=True)
                st.text_input("Código (Bloqueado)", p.get('codigo_bateria',''), disabled=True)
            with c2:
                npg = st.number_input("Precio Gral (S/)", value=float(p['precio_venta']), min_value=0.0, step=0.5)
                npp = st.number_input("Precio Punto (S/)", value=float(p.get('precio_punto') or 0.0), min_value=0.0, step=0.5)
                nimg = st.text_input("URL Imagen", value=p.get('imagen_url',''))
            
            st.divider()
            st.markdown(f"**Stock Actual:** {p['stock']}")
            mas = st.number_input("Cantidad a AÑADIR (+)", min_value=0, step=1)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("GUARDAR CAMBIOS", type="primary", use_container_width=True):
                with st.spinner('Guardando...'):
                    supabase.table("productos").update({"precio_venta":npg, "precio_punto":npp, "imagen_url":nimg, "stock": p['stock']+mas}).eq("id", p['id']).execute()
                    if mas > 0: supabase.table("historial").insert({"producto_nombre": p['nombre'], "cantidad": mas, "usuario": st.session_state.user, "tecnico": "Ingreso Stock", "local": "Almacén"}).execute()
                    time.sleep(1)
                st.success("✅ Guardado")
                time.sleep(0.5)
                st.rerun()
        
        st.markdown("---")
        if st.button("🗑️ ELIMINAR PRODUCTO", type="primary"): modal_borrar(p)

elif opcion == "Log":
    st.markdown("<h2>📜 Historial</h2>", unsafe_allow_html=True)
    logs = supabase.table("historial").select("*").order("fecha", desc=True).execute().data
    if logs:
        df = pd.DataFrame(logs)
        df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m/%Y %H:%M')
        st.dataframe(df[['fecha','producto_nombre','cantidad','usuario','tecnico','local']], use_container_width=True, hide_index=True)

elif opcion == "Stats":
    st.markdown("<h2>📊 Estadísticas</h2>", unsafe_allow_html=True)
    df = pd.DataFrame(supabase.table("productos").select("*").execute().data)
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Productos", len(df))
        c2.metric("Unidades en Stock", int(df['stock'].sum()))
        c3.metric("Valor Inventario", f"S/ {(df['stock']*df['precio_venta']).sum():,.2f}")

elif opcion == "Users":
    st.markdown("<h2>👥 Configuración</h2>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Usuarios", "Técnicos", "Locales"])
    with tab1:
        with st.form("u"):
            u = st.text_input("Usuario")
            p = st.text_input("Clave")
            r = st.selectbox("Rol", ["Normal", "Super"])
            if st.form_submit_button("Crear Usuario"):
                if supabase.table("usuarios").select("*").eq("usuario",u).execute().data: st.error("Existe")
                else: 
                    supabase.table("usuarios").insert({"usuario":u, "contrasena":p, "rol":r}).execute()
                    st.success("Creado")
    with tab2:
        with st.form("t"):
            tn = st.text_input("Nombre Técnico")
            if st.form_submit_button("Agregar"):
                supabase.table("tecnicos").insert({"nombre":tn}).execute()
                st.rerun()
        ts = supabase.table("tecnicos").select("*").execute().data
        if ts:
            col_a, col_b = st.columns([3,1])
            with col_a: t_del = st.selectbox("Borrar Técnico", [x['nombre'] for x in ts])
            with col_b: 
                st.write("")
                st.write("")
                if st.button("🗑️", key="bt"): modal_borrar_tecnico(t_del)
    with tab3:
        with st.form("l"):
            ln = st.text_input("Nombre Local")
            if st.form_submit_button("Agregar"):
                supabase.table("locales").insert({"nombre":ln}).execute()
                st.rerun()
        ls = supabase.table("locales").select("*").execute().data
        if ls:
            col_a, col_b = st.columns([3,1])
            with col_a: l_del = st.selectbox("Borrar Local", [x['nombre'] for x in ls])
            with col_b:
                st.write("")
                st.write("")
                if st.button("🗑️", key="bl"): modal_borrar_local(l_del)

elif opcion == "Prov":
    st.markdown("<h2>📞 Proveedores</h2>", unsafe_allow_html=True)
    provs = supabase.table("proveedores").select("*").execute().data
    if provs:
        for pr in provs:
            with st.container(border=True):
                st.markdown(f"**{pr['nombre_contacto']}**")
                st.link_button("WhatsApp", f"https://wa.me/{pr['whatsapp']}")
