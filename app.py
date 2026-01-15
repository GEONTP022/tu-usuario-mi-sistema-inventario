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

# --- CSS MAESTRO (FIX VISUAL + ALINEACIÓN) ---
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

    /* 3. ETIQUETAS, TEXTOS Y MODALES (NEGRO OBLIGATORIO) */
    div[data-testid="stWidgetLabel"] p, label, .stMarkdown p, h1, h2, h3, .stDialog p, .stDialog label, div[role="dialog"] p {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 700 !important;
    }

    /* 4. INPUTS Y CAJAS DE TEXTO (FIX VISIBILIDAD) */
    input, textarea, .stNumberInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border: 1px solid #999 !important;
        caret-color: #000000 !important;
    }
    /* Selectbox y desplegables */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #999 !important;
    }
    div[data-baseweb="select"] span { color: #000000 !important; -webkit-text-fill-color: #000000 !important; }
    ul[data-testid="stSelectboxVirtualDropdown"] li {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* 5. TARJETAS DE STOCK (ALINEACIÓN PERFECTA) */
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

    /* Imágenes centradas y contenidas */
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

    /* 6. BOTONES */
    div.stButton button {
        background-color: #2488bc !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: bold !important;
        width: 100% !important;
        margin-top: auto !important; /* Empuja el botón al fondo */
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
    
    /* Ventanas Flotantes (Modales) */
    div[role="dialog"] {
        background-color: #ffffff !important;
    }

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
        m = st.text_input("Marca (Opcional)")
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
                        "nombre": n, "categoria": c, "marca": m, "stock": s, "precio_venta": p, "imagen_url": img
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
        cols = st.columns(4)
        for i, p in enumerate(items):
            if (categoria == "Todos" or p['categoria'] == categoria) and (busqueda.lower() in p['nombre'].lower()):
                with cols[i % 4]:
                    with st.container(border=True):
                        # Imagen centrada
                        img_url = p.get('imagen_url') or "https://via.placeholder.com/150"
                        st.markdown(f"""
                            <div style="display: flex; justify-content: center; align-items: center; height: 160px; width: 100%; margin-bottom: 10px;">
                                <img src="{img_url}" style="max-height: 150px; width: auto; object-fit: contain; display: block;">
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # --- BLOQUE DE TEXTO CON ALTURA FIJA PARA ALINEACIÓN ---
                        # Esto asegura que todas las tarjetas tengan el mismo alto de texto
                        marca_html = f"<div style='color:#555; font-size:11px; font-weight:bold; text-transform:uppercase;'>{p.get('marca', '')}</div>" if p.get('marca') else "<div style='height:16px;'></div>"
                        
                        st.markdown(f"""
                            <div style="text-align:center; height:70px; display:flex; flex-direction:column; justify-content:flex-start; align-items:center;">
                                {marca_html}
                                <div style="color:black; font-weight:bold; font-size:15px; line-height:1.2; margin-top:2px;">{p['nombre']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        # -------------------------------------------------------

                        c1, c2 = st.columns(2)
                        with c1: st.markdown(f"<div style='text-align:center; color:black; font-size:13px;'>U: {p['stock']}</div>", unsafe_allow_html=True)
                        with c2: st.markdown(f"<div style='text-align:center; color:black; font-size:13px;'>S/ {p['precio_venta']}</div>", unsafe_allow_html=True)
                        
                        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                        
                        if p['stock'] > 0:
                            if st.button("SALIDA", key=f"s_{p['id']}", use_container_width=True):
                                modal_salida(p)
                        else:
                            st.button("🚫 NO STOCK", key=f"ns_{p['id']}", disabled=True, use_container_width=True)

elif opcion == "Carga":
    c_title, c_btn = st.columns([3, 1])
    with c_title: st.markdown("<h2>📥 Añadir / Reponer Stock</h2>", unsafe_allow_html=True)
    with c_btn:
        if st.button("➕ NUEVO PRODUCTO", use_container_width=True): modal_nuevo_producto()
    
    all_products = supabase.table("productos").select("*").order("nombre").execute().data
    nombres_prod = [p['nombre'] for p in all_products]
    
    seleccion = st.selectbox("Modelo / Repuesto (Busca aquí)", ["Seleccionar"] + nombres_prod)
    
    if seleccion != "Seleccionar":
        prod_data = next((item for item in all_products if item["nombre"] == seleccion), None)
        if prod_data:
            with st.form("form_update_stock"):
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    cat_opts = ["Pantallas", "Baterías", "Flex", "Glases", "Otros"]
                    idx_cat = cat_opts.index(prod_data['categoria']) if prod_data['categoria'] in cat_opts else 0
                    new_cat = st.selectbox("Categoría", cat_opts, index=idx_cat)
                    
                    marca_val = prod_data.get('marca') or ""
                    new_marca = st.text_input("Marca", value=marca_val) if new_cat in ["Pantallas", "Baterías", "Otros"] else marca_val

                with col_u2:
                    new_price = st.number_input("Precio Venta (S/)", value=float(prod_data['precio_venta']), min_value=0.0, step=0.5)
                    img_val = prod_data.get('imagen_url') or ""
                    new_img = st.text_input("URL Imagen", value=img_val)

                st.divider()
                st.markdown(f"**Stock Actual:** {prod_data['stock']}")
                stock_add = st.number_input("Cantidad a AÑADIR (+)", min_value=1, value=1, step=1)
                
                if st.form_submit_button("CONSOLIDAR INGRESO"):
                    total_stock = prod_data['stock'] + stock_add
                    supabase.table("productos").update({
                        "stock": total_stock, "precio_venta": new_price, "categoria": new_cat,
                        "marca": new_marca, "imagen_url": new_img
                    }).eq("id", prod_data['id']).execute()
                    
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

elif opcion == "Stats":
    st.markdown("<h2>📊 Estadísticas</h2>", unsafe_allow_html=True)
    p_data = supabase.table("productos").select("*").execute().data
    if p_data:
        df_p = pd.DataFrame(p_data)
        fig = px.pie(df_p, names='categoria', values='stock', hole=0.4, title="Stock por Categoría")
        st.plotly_chart(fig, use_container_width=True)

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

# --- RESET ---
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
