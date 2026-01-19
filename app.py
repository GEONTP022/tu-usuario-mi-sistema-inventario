import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, date
import time

# ==============================================================================
# 1. CONFIGURACIÓN INICIAL
# ==============================================================================
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except:
    st.error("⚠️ Error de conexión. Revisa los secrets.")
    st.stop()

st.set_page_config(page_title="VillaFix | Admin", page_icon="🛠️", layout="wide")

# ==============================================================================
# 2. CSS QUIRÚRGICO (SOLUCIÓN REAL)
# ==============================================================================
st.markdown("""
    <style>
    /* 1. OCULTAR BARRA DE COLORES SUPERIOR */
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    /* 2. OCULTAR EL BOTÓN DE MENU DE LA DERECHA (LOS 3 PUNTOS) Y DEPLOY */
    [data-testid="stToolbar"] {
        visibility: hidden !important;
        display: none !important;
    }
    .stDeployButton {
        display: none !important;
    }
    
    /* 3. HACER TRANSPARENTE LA CABECERA PERO MANTENER LA FLECHA */
    header {
        background-color: transparent !important;
    }
    
    /* 4. ASEGURAR QUE LA FLECHA DEL MENÚ (IZQUIERDA) SE VEA */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        visibility: visible !important;
        color: #000000 !important;
        background-color: white !important;
        border-radius: 50%;
        padding: 2px;
    }
    
    /* 5. OCULTAR FOOTER "MADE WITH STREAMLIT" */
    footer {
        visibility: hidden !important;
        display: none !important;
        height: 0px !important;
    }
    
    /* 6. SUBIR EL CONTENIDO PARA QUITAR ESPACIO VACÍO ARRIBA */
    .block-container {
        padding-top: 1rem !important;
    }
    
    /* 7. ESTILOS GENERALES */
    .stApp { background-color: #ffffff !important; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #1a222b !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
    [data-testid="stSidebar"] button { background-color: transparent !important; border: none !important; color: #bdc3c7 !important; text-align: left !important; padding-left: 15px !important; transition: 0.3s; }
    [data-testid="stSidebar"] button:hover { background-color: rgba(255,255,255,0.05) !important; border-left: 4px solid #3498db !important; color: #ffffff !important; padding-left: 25px !important; }
    
    /* Tarjetas y Textos */
    div[data-testid="stVerticalBlockBorderWrapper"] { background-color: #ffffff !important; border: 1px solid #ddd !important; padding: 10px !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important; }
    div[data-testid="stMetricValue"] { color: #2488bc !important; }
    div[data-testid="stWidgetLabel"] p, label, .stMarkdown h1, h2, h3 { color: #000000 !important; }
    
    /* Inputs */
    input, textarea { background-color: #ffffff !important; color: black !important; border: 1px solid #ccc !important; }
    input:disabled { background-color: #f0f2f6 !important; color: #555 !important; }
    
    /* Botones */
    div.stButton button { background-color: #2488bc !important; color: white !important; border: none !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. LÓGICA DE SESIÓN
# ==============================================================================
SESSION_DURATION = 12 * 3600 

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.rol = None
    st.session_state.user = None
    st.session_state.menu = "Stock"
    st.session_state.login_time = 0

# Anti-Refresco
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

# Verificar tiempo
if st.session_state.autenticado:
    if (time.time() - st.session_state.login_time) > SESSION_DURATION:
        st.session_state.autenticado = False
        st.query_params.clear()
        st.rerun()

# --- LOGIN ---
if not st.session_state.autenticado:
    st.markdown("""<style>.stApp {background-image: url('https://img.freepik.com/free-vector/gradient-technological-background_23-2148884155.jpg?w=1380'); background-size: cover;}</style>""", unsafe_allow_html=True)
    st.markdown("<br><br><h1 style='text-align:center; color:white; text-shadow: 2px 2px 4px #000000;'>VILLAFIX SYSTEM</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        with st.container(border=True):
            st.markdown("<h3 style='text-align:center;'>Acceso Seguro</h3>", unsafe_allow_html=True)
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
# 4. FUNCIONES Y SIDEBAR
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

# MODALES
@st.dialog("Gestionar Inventario")
def modal_gestion(producto):
    st.markdown(f"### {producto['nombre']}")
    tab_salida, tab_devolucion = st.tabs(["📉 SALIDA", "↩️ DEVOLUCIÓN"])
    
    with tab_salida:
        st.write(f"**Stock:** {producto['stock']}")
        try: techs = [t['nombre'] for t in supabase.table("tecnicos").select("nombre").execute().data]
        except: techs = ["General"]
        try: locs = [l['nombre'] for l in supabase.table("locales").select("nombre").execute().data]
        except: locs = ["Principal"]

        # Sin form para evitar enter
        t = st.selectbox("Técnico", ["Seleccionar"] + techs, key="ts")
        l = st.selectbox("Local", ["Seleccionar"] + locs, key="ls")
        c = st.number_input("Cantidad", 1, max(1, producto['stock']), 1, key="cs")
        
        if st.button("CONFIRMAR SALIDA", use_container_width=True):
            if producto['stock'] <= 0: st.error("Sin stock.")
            elif t == "Seleccionar" or l == "Seleccionar": st.error("Faltan datos.")
            else:
                supabase.table("productos").update({"stock": producto['stock'] - c}).eq("id", producto['id']).execute()
                supabase.table("historial").insert({"producto_nombre": producto['nombre'], "cantidad": -c, "usuario": st.session_state.user, "tecnico": t, "local": l}).execute()
                st.success("Listo"); time.sleep(0.5); st.rerun()

    with tab_devolucion:
        r = st.text_input("Motivo", "Devolución")
        cd = st.number_input("Cantidad", 1, step=1, key="cd")
        if st.button("INGRESAR", use_container_width=True):
            supabase.table("productos").update({"stock": producto['stock'] + cd}).eq("id", producto['id']).execute()
            supabase.table("historial").insert({"producto_nombre": producto['nombre'], "cantidad": cd, "usuario": st.session_state.user, "tecnico": r, "local": "Almacén"}).execute()
            st.success("Listo"); time.sleep(0.5); st.rerun()

@st.dialog("Nuevo Producto")
def modal_nuevo_producto():
    st.markdown("### Crear")
    n = st.text_input("Nombre *")
    c1, c2 = st.columns(2)
    with c1: cat = st.selectbox("Categoría", ["Pantallas", "Baterías", "Flex", "Glases", "Otros"])
    with c2: m = st.text_input("Marca")
    cod = st.text_input("Código")
    s = st.number_input("Stock", 0)
    p1, p2 = st.columns(2)
    with p1: pg = st.number_input("Precio Gral", 0.0)
    with p2: pp = st.number_input("Precio Punto", 0.0)
    img = st.text_input("URL Imagen")
    
    if st.button("GUARDAR", type="primary", use_container_width=True):
        if not n or pg <= 0: st.error("Faltan datos")
        else:
            q = supabase.table("productos").select("id").eq("nombre", n).eq("marca", m).eq("categoria", cat)
            if cod: q = q.eq("codigo_bateria", cod)
            else: q = q.eq("codigo_bateria", "")
            if q.execute().data: st.error("Duplicado")
            else:
                supabase.table("productos").insert({"nombre": n, "categoria": cat, "marca": m, "codigo_bateria": cod, "stock": s, "precio_venta": pg, "precio_punto": pp, "imagen_url": img}).execute()
                supabase.table("historial").insert({"producto_nombre": n, "cantidad": s, "usuario": st.session_state.user, "tecnico": "Inicio", "local": "Almacén"}).execute()
                st.success("Creado"); time.sleep(0.5); st.rerun()

@st.dialog("Eliminar")
def modal_borrar(p):
    st.write(f"¿Borrar {p['nombre']}?")
    if st.button("SÍ, BORRAR", type="primary"):
        supabase.table("productos").delete().eq("id", p['id']).execute()
        st.success("Borrado"); time.sleep(0.5); st.rerun()

# SIDEBAR
with st.sidebar:
    st.markdown(f"<div class='profile-section'><img src='https://cdn-icons-png.flaticon.com/512/3135/3135715.png' class='profile-pic'><p style='color:white;text-align:center;'>{st.session_state.user.upper()}</p></div>", unsafe_allow_html=True)
    if st.button("📊 Stock"): st.session_state.menu = "Stock"
    if st.session_state.rol == "Super":
        if st.button("📥 Carga/Edit"): st.session_state.menu = "Carga"
        if st.button("📋 Historial"): st.session_state.menu = "Log"
        if st.button("📈 Stats"): st.session_state.menu = "Stats"
        if st.button("👥 Config"): st.session_state.menu = "Users"
        if st.button("📞 Proveedores"): st.session_state.menu = "Prov"
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Salir"):
        st.session_state.autenticado = False
        st.query_params.clear()
        st.rerun()

# ==============================================================================
# 5. VISTAS
# ==============================================================================
opcion = st.session_state.menu

if opcion == "Stock":
    st.title("Inventario General")
    c1, c2 = st.columns([3, 1])
    with c1: bus = st.text_input("Buscar...")
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
                        st.markdown(f"<div style='display:flex;justify-content:center;height:120px;'><img src='{u_img}' style='max-height:100px;'></div>", unsafe_allow_html=True)
                        st.markdown(f"**{p['nombre']}**")
                        st.caption(f"{p.get('marca','')} | {p.get('codigo_bateria','')}")
                        k1, k2, k3 = st.columns([1, 1.5, 1.5])
                        k1.markdown(f"**Stk**<br>{p['stock']}", unsafe_allow_html=True)
                        k2.markdown(f"**Gral**<br>{p['precio_venta']}", unsafe_allow_html=True)
                        k3.markdown(f"**Pto**<br>{p.get('precio_punto','--')}", unsafe_allow_html=True)
                        if p['stock'] > 0: 
                            if st.button("SALIDA", key=f"s{p['id']}", use_container_width=True): modal_gestion(p)
                        else: st.button("AGOTADO", disabled=True, key=f"n{p['id']}", use_container_width=True)

elif opcion == "Carga":
    st.title("Gestión de Stock")
    if st.button("➕ NUEVO", type="primary"): modal_nuevo_producto()
    
    prods = supabase.table("productos").select("*").order("nombre").execute().data
    lista = [f"{p['nombre']} - {p.get('marca','')}" for p in prods]
    sel = st.selectbox("Editar:", ["Seleccionar"] + lista)
    
    if sel != "Seleccionar":
        p = prods[lista.index(sel)]
        with st.container(border=True):
            st.markdown(f"### {p['nombre']}")
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Categoría", p['categoria'], disabled=True)
                st.text_input("Marca", p.get('marca',''), disabled=True)
                st.text_input("Código", p.get('codigo_bateria',''), disabled=True)
            with c2:
                npg = st.number_input("Precio Gral", value=float(p['precio_venta']))
                npp = st.number_input("Precio Punto", value=float(p.get('precio_punto') or 0.0))
                nimg = st.text_input("Imagen URL", value=p.get('imagen_url',''))
            
            mas = st.number_input("Añadir Stock (+)", 0)
            if st.button("GUARDAR CAMBIOS", type="primary"):
                supabase.table("productos").update({"precio_venta":npg, "precio_punto":npp, "imagen_url":nimg, "stock": p['stock']+mas}).eq("id", p['id']).execute()
                if mas > 0: supabase.table("historial").insert({"producto_nombre": p['nombre'], "cantidad": mas, "usuario": st.session_state.user, "tecnico": "Ingreso", "local": "Almacén"}).execute()
                st.success("Guardado"); time.sleep(0.5); st.rerun()
        if st.button("Eliminar Producto"): modal_borrar(p)

elif opcion == "Log":
    st.title("Historial")
    logs = supabase.table("historial").select("*").order("fecha", desc=True).execute().data
    if logs:
        df = pd.DataFrame(logs)
        df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m/%Y %H:%M')
        st.dataframe(df[['fecha','producto_nombre','cantidad','usuario','tecnico','local']], use_container_width=True)

elif opcion == "Stats":
    st.title("Estadísticas")
    df = pd.DataFrame(supabase.table("productos").select("*").execute().data)
    if not df.empty:
        c1, c2 = st.columns(2)
        c1.metric("Total Items", len(df))
        c2.metric("Valor Inventario", f"S/ {(df['stock']*df['precio_venta']).sum():,.2f}")

elif opcion == "Users":
    st.title("Configuración")
    with st.form("u"):
        u = st.text_input("Usuario")
        p = st.text_input("Clave")
        r = st.selectbox("Rol", ["Normal", "Super"])
        if st.form_submit_button("Crear Usuario"):
            supabase.table("usuarios").insert({"usuario":u, "contrasena":p, "rol":r}).execute()
            st.success("Creado")

elif opcion == "Prov":
    st.title("Proveedores")
    pr = supabase.table("proveedores").select("*").execute().data
    for p in pr: st.write(f"**{p['nombre_contacto']}**")
