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

# --- CSS MAESTRO (TU DISEÑO PERFECTO) ---
st.markdown("""
    <style>
    /* 1. FONDO BLANCO GLOBAL */
    .stApp, .main, .block-container {
        background-color: #ffffff !important;
    }

    /* 2. BARRA LATERAL (OSCURA Y LIMPIA) */
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

    /* 3. ETIQUETAS Y TEXTOS DEL FORMULARIO (NEGROS) */
    div[data-testid="stWidgetLabel"] p, label, .stMarkdown p, h1, h2, h3, .stDialog p, .stDialog label {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 700 !important;
    }

    /* 4. INPUTS */
    input, textarea, .stNumberInput input {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        border: 1px solid #aaa !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        border: 1px solid #aaa !important;
    }
    div[data-baseweb="select"] span { color: #000000 !important; }
    ul[data-testid="stSelectboxVirtualDropdown"] li {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* 5. TARJETAS DE STOCK */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 1px solid #ddd !important;
        padding: 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        height: 100% !important; 
    }

    /* IMÁGENES: CENTRADO FORZADO */
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
        flex-grow: 0 !important;
    }

    /* Textos dentro de tarjetas (Negro) */
    div[data-testid="column"] div[data-testid="stVerticalBlockBorderWrapper"] p,
    div[data-testid="column"] div[data-testid="stVerticalBlockBorderWrapper"] div {
        color: #000000 !important;
    }

    /* 6. BOTONES */
    div.stButton button {
        background-color: #2488bc !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: bold !important;
        width: 100% !important;
    }
    div.stButton button p { color: #ffffff !important; }

    /* Botón NO STOCK (ROJO) */
    div.stButton button:disabled {
        background-color: #e74c3c !important;
        color: white !important;
        opacity: 1 !important;
        cursor: not-allowed !important;
        border: 1px solid #c0392b !important;
    }
    div.stButton button:disabled p {
        color: white !important;
    }
    
    /* Pestañas (Tabs) en Usuarios */
    button[data-baseweb="tab"] {
        color: #000000 !important;
    }
    div[data-baseweb="tab-list"] {
        background-color: #f1f3f4 !important;
        border-radius: 8px;
    }

    /* Perfil */
    .profile-section { text-align: center !important; padding: 20px 0px; }
    .profile-pic { width: 100px; height: 100px; border-radius: 50%; border: 3px solid #f39c12; object-fit: cover; display: block; margin: 0 auto 10px auto; }

    [data-testid="stSidebarNav"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# --- VENTANA FLOTANTE (MODAL) PARA SALIDA ---
@st.dialog("Registrar Salida de Producto")
def modal_salida(producto):
    st.markdown(f"**Producto:** {producto['nombre']}")
    st.markdown(f"**Stock Actual:** {producto['stock']}")
    
    # Obtener listas de técnicos y locales (o usar default si falla)
    try:
        techs = [t['nombre'] for t in supabase.table("tecnicos").select("nombre").execute().data]
    except:
        techs = ["Técnico General"] # Default si no hay tabla
        
    try:
        locs = [l['nombre'] for l in supabase.table("locales").select("nombre").execute().data]
    except:
        locs = ["Local Principal"] # Default si no hay tabla

    with st.form("form_salida_modal"):
        tecnico = st.selectbox("Técnico que solicita", ["Seleccionar"] + techs)
        local = st.selectbox("Local de destino", ["Seleccionar"] + locs)
        cantidad = st.number_input("Unidades a retirar", min_value=1, max_value=producto['stock'], step=1)
        
        submitted = st.form_submit_button("CONFIRMAR SALIDA")
        
        if submitted:
            if tecnico == "Seleccionar" or local == "Seleccionar":
                st.error("⚠️ Seleccione Técnico y Local.")
            else:
                # Actualizar Stock
                nuevo_stock = producto['stock'] - cantidad
                supabase.table("productos").update({"stock": nuevo_stock}).eq("id", producto['id']).execute()
                
                # Guardar Historial con datos extra
                supabase.table("historial").insert({
                    "producto_nombre": producto['nombre'],
                    "cantidad": -cantidad,
                    "usuario": st.session_state.user,
                    "tecnico": tecnico, # Asegurate que esta columna exista en Supabase
                    "local": local      # Asegurate que esta columna exista en Supabase
                }).execute()
                
                st.success("Salida registrada.")
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
                        st.image(p.get('imagen_url') or "https://via.placeholder.com/150", use_column_width=False)
                        st.markdown(f"<div style='text-align:center; color:#000000; font-weight:bold; margin-bottom:5px; height:45px; overflow:hidden; display:flex; align-items:center; justify-content:center; line-height:1.2;'>{p['nombre']}</div>", unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        with c1: st.markdown(f"<div style='text-align:center; color:#000000; font-size:13px;'>U: {p['stock']}</div>", unsafe_allow_html=True)
                        with c2: st.markdown(f"<div style='text-align:center; color:#000000; font-size:13px;'>S/ {p['precio_venta']}</div>", unsafe_allow_html=True)
                        
                        st.markdown("<div style='margin-top:5px;'></div>", unsafe_allow_html=True)
                        
                        if p['stock'] > 0:
                            # AQUI ESTA EL CAMBIO: Llama a la ventana flotante
                            if st.button("SALIDA", key=f"s_{p['id']}", use_container_width=True):
                                modal_salida(p)
                        else:
                            st.button("🚫 NO STOCK", key=f"ns_{p['id']}", disabled=True, use_container_width=True)

elif opcion == "Carga":
    st.markdown("<h2>📥 Añadir Producto</h2>", unsafe_allow_html=True)
    with st.form("form_carga", clear_on_submit=True):
        st.markdown("<p>Complete los campos obligatorios (*)</p>", unsafe_allow_html=True)
        
        n = st.text_input("Modelo / Repuesto *")
        c = st.selectbox("Categoría *", ["Seleccionar", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])
        s = st.number_input("Cantidad a añadir", min_value=1, step=1)
        p = st.number_input("Precio Venta (S/) *", min_value=0.0, step=0.5)
        img = st.text_input("URL Imagen (Opcional)")
        
        if st.form_submit_button("CONSOLIDAR INGRESO", use_container_width=True):
            if not n or c == "Seleccionar" or p <= 0:
                st.warning("⚠️ Falta completar Nombre, Categoría o Precio.")
            else:
                existe = supabase.table("productos").select("*").eq("nombre", n).execute()
                if existe.data:
                    nuevo_stock = existe.data[0]['stock'] + s
                    supabase.table("productos").update({"stock": nuevo_stock, "precio_venta": p, "imagen_url": img}).eq("id", existe.data[0]['id']).execute()
                    st.success(f"✅ Stock actualizado!")
                else:
                    supabase.table("productos").insert({"nombre": n, "categoria": c, "stock": s, "precio_venta": p, "imagen_url": img}).execute()
                    st.success(f"✅ Creado!")
                supabase.table("historial").insert({"producto_nombre": n, "cantidad": s, "usuario": st.session_state.user}).execute()

elif opcion == "Log":
    st.markdown("<h2>📜 Historial</h2>", unsafe_allow_html=True)
    # Intenta traer tecnico y local si existen, sino trae todo
    logs = supabase.table("historial").select("*").order("fecha", desc=True).execute().data
    if logs:
        df = pd.DataFrame(logs)
        df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m/%Y %H:%M')
        # Mostrar columnas nuevas si existen en el dataframe
        cols_to_show = ['fecha', 'producto_nombre', 'cantidad', 'usuario']
        if 'tecnico' in df.columns: cols_to_show.append('tecnico')
        if 'local' in df.columns: cols_to_show.append('local')
        
        st.dataframe(df[cols_to_show], use_container_width=True, hide_index=True)

elif opcion == "Stats":
    st.markdown("<h2>📊 Estadísticas</h2>", unsafe_allow_html=True)
    p_data = supabase.table("productos").select("*").execute().data
    if p_data:
        df_p = pd.DataFrame(p_data)
        fig = px.pie(df_p, names='categoria', values='stock', hole=0.4, title="Stock por Categoría")
        st.plotly_chart(fig, use_container_width=True)

elif opcion == "Users":
    st.markdown("<h2>👥 Gestión de Usuarios y Datos</h2>", unsafe_allow_html=True)
    
    # PESTAÑAS PARA ORGANIZAR LA GESTIÓN
    tab1, tab2, tab3 = st.tabs(["🔑 Accesos Sistema", "👨‍🔧 Técnicos", "🏠 Locales"])
    
    with tab1:
        with st.form("nu"):
            st.write("Crear nuevo acceso al sistema")
            un = st.text_input("Usuario")
            pw = st.text_input("Clave")
            rl = st.selectbox("Rol", ["Normal", "Super"])
            if st.form_submit_button("CREAR USUARIO"):
                supabase.table("usuarios").insert({"usuario":un, "contrasena":pw, "rol":rl}).execute()
                st.success("Usuario creado.")
    
    with tab2:
        st.write("Registrar técnicos para las salidas")
        with st.form("nt"):
            tec_name = st.text_input("Nombre del Técnico")
            if st.form_submit_button("AGREGAR TÉCNICO"):
                # Asegurate de tener la tabla 'tecnicos' en Supabase
                try:
                    supabase.table("tecnicos").insert({"nombre": tec_name}).execute()
                    st.success("Técnico agregado.")
                except:
                    st.error("Error: Verifica que exista la tabla 'tecnicos' en Supabase.")
        # Lista de técnicos actuales
        try:
            tecs = supabase.table("tecnicos").select("*").execute().data
            if tecs: st.dataframe(pd.DataFrame(tecs), use_container_width=True, hide_index=True)
        except: pass

    with tab3:
        st.write("Registrar locales de destino")
        with st.form("nl"):
            loc_name = st.text_input("Nombre del Local")
            if st.form_submit_button("AGREGAR LOCAL"):
                try:
                    supabase.table("locales").insert({"nombre": loc_name}).execute()
                    st.success("Local agregado.")
                except:
                    st.error("Error: Verifica que exista la tabla 'locales' en Supabase.")
        # Lista de locales actuales
        try:
            locs = supabase.table("locales").select("*").execute().data
            if locs: st.dataframe(pd.DataFrame(locs), use_container_width=True, hide_index=True)
        except: pass

elif opcion == "Prov":
    st.markdown("<h2>📞 Proveedores</h2>", unsafe_allow_html=True)
    provs = supabase.table("proveedores").select("*").execute().data
    if provs:
        for pr in provs:
            with st.container(border=True):
                st.markdown(f"**{pr['nombre_contacto']}**")
                st.link_button("WhatsApp", f"https://wa.me/{pr['whatsapp']}")

# --- RESET OCULTO ---
elif opcion == "Reset":
    st.markdown("<h2>⚙️ Zona de Peligro</h2>", unsafe_allow_html=True)
    st.warning("⚠️ Estas acciones no se pueden deshacer.")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.error("Eliminar Inventario")
        if st.button("BORRAR STOCK TOTAL", use_container_width=True):
            data = supabase.table("productos").select("id").execute().data
            for item in data: supabase.table("productos").delete().eq("id", item['id']).execute()
            st.success("Hecho.")

    with col_r2:
        st.error("Eliminar Historial")
        if st.button("BORRAR HISTORIAL TOTAL", use_container_width=True):
            data = supabase.table("historial").select("id").execute().data
            for item in data: supabase.table("historial").delete().eq("id", item['id']).execute()
            st.success("Hecho.")
