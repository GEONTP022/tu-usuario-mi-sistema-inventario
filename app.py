import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, date
import time

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

# --- FUNCIÓN DE BÚSQUEDA INTELIGENTE ---
def es_coincidencia(busqueda, texto_db):
    if not busqueda: return True 
    if not texto_db: return False
    
    b = str(busqueda).lower().strip()
    
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

# --- CSS LIMPIO (SIN EL CÓDIGO QUE ROMPÍA LA PANTALLA) ---
st.markdown("""
    <style>
    /* Configuración básica */
    .stApp { background-color: #ffffff; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #1a222b; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
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
    
    /* Textos generales en negro */
    h1, h2, h3, p, label, .stMetricValue, .stMarkdown { color: #000000 !important; }
    
    /* Botones Azules */
    div.stButton button { 
        background-color: #2488bc !important; 
        color: #ffffff !important; 
        font-weight: bold; 
        border: none;
    }
    /* Botones Rojos (Disabled) */
    div.stButton button:disabled { 
        background-color: #e74c3c !important; 
        color: white !important; 
        opacity: 1 !important; 
    }
    
    /* Imágenes controladas */
    div[data-testid="stImage"] {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 10px;
    }
    div[data-testid="stImage"] img {
        object-fit: contain;
        max-height: 150px;
    }

    [data-testid="stSidebarNav"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# --- VENTANAS FLOTANTES ---

@st.dialog("Gestionar Inventario")
def modal_gestion(producto):
    st.markdown(f"### {producto['nombre']}")
    tab_salida, tab_devolucion = st.tabs(["📉 REGISTRAR SALIDA", "↩️ DEVOLUCIÓN / INGRESO"])
    
    with tab_salida:
        st.write(f"**Stock Actual:** {producto['stock']}")
        try: techs = [t['nombre'] for t in supabase.table("tecnicos").select("nombre").execute().data]
        except: techs = ["General"]
        try: locs = [l['nombre'] for l in supabase.table("locales").select("nombre").execute().data]
        except: locs = ["Principal"]

        with st.form("form_salida_modal"):
            tecnico = st.selectbox("Técnico", ["Seleccionar"] + techs, key="tec_sal")
            local = st.selectbox("Local", ["Seleccionar"] + locs, key="loc_sal")
            max_val = producto['stock'] if producto['stock'] > 0 else 1
            cantidad = st.number_input("Cantidad a RETIRAR", min_value=1, max_value=max_val, step=1, key="cant_sal")
            
            if st.form_submit_button("CONFIRMAR SALIDA"):
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
                    st.success("✅ Listo")
                    time.sleep(0.5)
                    st.rerun()

    with tab_devolucion:
        st.info("Ingreso rápido o devolución.")
        with st.form("form_devolucion_modal"):
            razon = st.text_input("Motivo", value="Devolución")
            cant_dev = st.number_input("Cantidad a INGRESAR", min_value=1, step=1, key="cant_dev")
            
            if st.form_submit_button("CONFIRMAR DEVOLUCIÓN"):
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
                st.success("✅ Listo")
                time.sleep(0.5)
                st.rerun()

@st.dialog("✨ Nuevo Producto")
def modal_nuevo_producto():
    st.markdown("### Crear Producto")
    with st.form("form_nuevo_prod"):
        n = st.text_input("Nombre / Modelo *")
        c = st.selectbox("Categoría *", ["Seleccionar", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])
        m = st.text_input("Marca")
        cb = st.text_input("Código de Batería (Si aplica)")
        s = st.number_input("Stock Inicial *", min_value=0, step=1)
        
        col_p1, col_p2 = st.columns(2)
        with col_p1: p_gen = st.number_input("Precio General (S/) *", min_value=0.0, step=0.5)
        with col_p2: p_punto = st.number_input("Precio Punto (S/)", min_value=0.0, step=0.5)
        
        img = st.text_input("URL Imagen (Opcional)")

        if st.form_submit_button("GUARDAR"):
            if not n or c == "Seleccionar" or p_gen <= 0:
                st.error("⚠️ Datos incompletos.")
            else:
                # --- VALIDACIÓN EXACTA (Nombre + Marca + Categoria + Codigo) ---
                query = supabase.table("productos").select("id")\
                    .eq("nombre", n).eq("marca", m).eq("categoria", c)
                
                # Manejar código vacío o lleno
                if cb: query = query.eq("codigo_bateria", cb)
                else: query = query.eq("codigo_bateria", "") # Ojo: Asegúrate de guardar cadenas vacías si no hay código

                existe = query.execute()

                if existe.data:
                    st.error("⚠️ Ya existe este producto EXACTO (Mismo nombre, marca, categoría y código).")
                else:
                    with st.spinner('Guardando...'):
                        supabase.table("productos").insert({
                            "nombre": n, "categoria": c, "marca": m, "codigo_bateria": cb,
                            "stock": s, "precio_venta": p_gen, "precio_punto": p_punto, "imagen_url": img
                        }).execute()
                        supabase.table("historial").insert({
                            "producto_nombre": n, "cantidad": s, "usuario": st.session_state.user,
                            "tecnico": "Ingreso Inicial", "local": "Almacén"
                        }).execute()
                    st.success("✅ Creado")
                    time.sleep(0.5)
                    st.rerun()

@st.dialog("⚠️ Eliminar")
def modal_borrar_producto(producto):
    st.write(f"¿Eliminar **{producto['nombre']}** permanentemente?")
    if st.button("SÍ, ELIMINAR", type="primary"):
        with st.spinner('Eliminando...'):
            supabase.table("productos").delete().eq("id", producto['id']).execute()
        st.success("✅ Eliminado")
        time.sleep(0.5)
        st.rerun()

@st.dialog("⚠️ Eliminar")
def modal_borrar_tecnico(nombre):
    st.write(f"¿Eliminar {nombre}?")
    if st.button("SÍ, ELIMINAR"):
        supabase.table("tecnicos").delete().eq("nombre", nombre).execute()
        st.rerun()

@st.dialog("⚠️ Eliminar")
def modal_borrar_local(nombre):
    st.write(f"¿Eliminar {nombre}?")
    if st.button("SÍ, ELIMINAR"):
        supabase.table("locales").delete().eq("nombre", nombre).execute()
        st.rerun()

# --- PANEL IZQUIERDO ---
with st.sidebar:
    st.markdown(f"""
        <div class="profile-section">
            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" class="profile-pic">
            <p style="font-size:18px; font-weight:bold; margin:0; color:white;">{st.session_state.user.upper()}</p>
            <p style="font-size:12px; color:#f39c12; margin:0;">{st.session_state.rol.upper()} USER</p>
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
    st.markdown("## Inventario General")
    col_a, col_b = st.columns([3, 1])
    with col_a: 
        busqueda = st.text_input("Buscar...", placeholder="Ej: ip11, Samsung, celda...")
    with col_b: 
        categoria = st.selectbox("Categoría", ["Todos", "⚠️ Solo Bajo Stock", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])

    items = supabase.table("productos").select("*").order("nombre").execute().data
    if items:
        filtered_items = []
        for p in items:
            coincide = es_coincidencia(busqueda, p['nombre']) or \
                       es_coincidencia(busqueda, p.get('marca')) or \
                       es_coincidencia(busqueda, p.get('codigo_bateria'))
            
            match_cat = True
            if categoria == "⚠️ Solo Bajo Stock": match_cat = (p['stock'] <= 2)
            elif categoria != "Todos": match_cat = (p['categoria'] == categoria)
                
            if coincide and match_cat: filtered_items.append(p)
        
        if busqueda:
            b_clean = busqueda.lower().strip()
            filtered_items.sort(key=lambda x: 0 if x['nombre'].lower().startswith(b_clean) else 1)

        # --- GRID SYSTEM NATIVO (NO SE ROMPE) ---
        N_COLS = 4
        # Dividir en filas de 4 para que Streamlit renderice bloques limpios
        rows = [filtered_items[i:i + N_COLS] for i in range(0, len(filtered_items), N_COLS)]
        
        for row in rows:
            cols = st.columns(N_COLS)
            for i, p in enumerate(row):
                with cols[i]:
                    with st.container(border=True):
                        # Imagen
                        img = p.get('imagen_url') or "https://via.placeholder.com/150"
                        st.image(img, use_column_width=True)
                        
                        # Datos
                        st.markdown(f"**{p['nombre']}**")
                        if p.get('marca'): st.caption(f"{p['marca']}")
                        if p.get('codigo_bateria'): st.caption(f"Cod: {p['codigo_bateria']}")
                        
                        # Precios y Stock (Diseño de 3 columnas)
                        c1, c2, c3 = st.columns([1, 1.2, 1.2])
                        with c1: st.markdown(f"**Stock**<br>{p['stock']}", unsafe_allow_html=True)
                        with c2: st.markdown(f"**Gral**<br>S/{p['precio_venta']}", unsafe_allow_html=True)
                        with c3:
                            val_punto = p.get('precio_punto', 0)
                            color_punto = "#27ae60" if val_punto else "#bdc3c7"
                            val_str = f"S/{val_punto}" if val_punto else "--"
                            st.markdown(f"<span style='color:{color_punto}'>**Punto**<br>{val_str}</span>", unsafe_allow_html=True)
                        
                        st.markdown("")
                        # Botón
                        if p['stock'] > 0:
                            if st.button("SALIDA", key=f"btn_{p['id']}", use_container_width=True):
                                modal_gestion(p)
                        else:
                            st.button("🚫 NO STOCK", key=f"btn_no_{p['id']}", disabled=True, use_container_width=True)

elif opcion == "Carga":
    st.markdown("## 📥 Gestión de Stock")
    c1, c2 = st.columns([3, 1])
    with c2:
        if st.button("➕ NUEVO PRODUCTO", use_container_width=True): modal_nuevo_producto()
    
    all_products = supabase.table("productos").select("*").order("nombre").execute().data
    opciones = {f"{p['nombre']} ({p.get('marca','')})": p for p in all_products}
    
    seleccion = st.selectbox("Buscar para editar/reponer:", ["Seleccionar"] + list(opciones.keys()))
    
    if seleccion != "Seleccionar":
        prod = opciones[seleccion]
        with st.container(border=True):
            st.subheader(f"Editando: {prod['nombre']}")
            with st.form("edit_form"):
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    new_cat = st.selectbox("Categoría", ["Pantallas", "Baterías", "Flex", "Glases", "Otros"], index=["Pantallas", "Baterías", "Flex", "Glases", "Otros"].index(prod['categoria']))
                    new_marca = st.text_input("Marca", value=prod.get('marca', ''))
                    new_cod = st.text_input("Código Batería", value=prod.get('codigo_bateria', ''))
                with col_u2:
                    new_p_gen = st.number_input("Precio Gral", value=float(prod['precio_venta']), step=0.5)
                    # Handle possible missing column gracefully just in case
                    current_punto = float(prod.get('precio_punto') or 0.0)
                    new_p_punto = st.number_input("Precio Punto", value=current_punto, step=0.5)
                    new_img = st.text_input("Imagen URL", value=prod.get('imagen_url', ''))
                
                st.divider()
                add_stock = st.number_input("AÑADIR STOCK (+)", value=0, step=1)
                
                if st.form_submit_button("GUARDAR CAMBIOS"):
                    with st.spinner("Actualizando..."):
                        new_total = prod['stock'] + add_stock
                        supabase.table("productos").update({
                            "categoria": new_cat, "marca": new_marca, "codigo_bateria": new_cod,
                            "precio_venta": new_p_gen, "precio_punto": new_p_punto, 
                            "imagen_url": new_img, "stock": new_total
                        }).eq("id", prod['id']).execute()
                        
                        if add_stock > 0:
                            supabase.table("historial").insert({
                                "producto_nombre": prod['nombre'], "cantidad": add_stock,
                                "usuario": st.session_state.user, "tecnico": "Ingreso Stock", "local": "Almacén"
                            }).execute()
                    st.success("Actualizado")
                    time.sleep(0.5)
                    st.rerun()
            
            if st.button("🗑️ Borrar Producto"):
                modal_borrar_producto(prod)

elif opcion == "Log":
    st.markdown("## 📜 Historial")
    today = datetime.now()
    d_range = st.date_input("Filtrar fecha:", (today - timedelta(days=30), today))
    
    logs = supabase.table("historial").select("*").order("fecha", desc=True).execute().data
    if logs:
        df = pd.DataFrame(logs)
        # FIX DE FECHAS: Normalizar a solo fecha (sin hora) para comparar
        df['dt'] = pd.to_datetime(df['fecha']).dt.date
        if len(d_range) == 2:
            df = df[(df['dt'] >= d_range[0]) & (df['dt'] <= d_range[1])]
        
        # Formato legible
        df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m/%Y %H:%M')
        st.dataframe(
            df[['fecha', 'producto_nombre', 'cantidad', 'usuario', 'tecnico', 'local']], 
            use_container_width=True, 
            hide_index=True
        )

elif opcion == "Stats":
    st.markdown("## 📊 Estadísticas")
    dr = st.date_input("Periodo:", (datetime.now()-timedelta(days=30), datetime.now()))
    
    prods = supabase.table("productos").select("*").execute().data
    hists = supabase.table("historial").select("*").execute().data
    
    if prods:
        df_p = pd.DataFrame(prods)
        k1, k2, k3 = st.columns(3)
        k1.metric("Unidades Totales", df_p['stock'].sum())
        k2.metric("Valor Inventario (Gral)", f"S/ {(df_p['stock'] * df_p['precio_venta']).sum():,.2f}")
        k3.metric("Referencias", len(df_p))
        
        if hists:
            df_h = pd.DataFrame(hists)
            # FIX DE FECHAS EN STATS
            df_h['dt'] = pd.to_datetime(df_h['fecha']).dt.date
            if len(dr) == 2:
                df_h = df_h[(df_h['dt'] >= dr[0]) & (df_h['dt'] <= dr[1])]
            
            salidas = df_h[df_h['cantidad'] < 0].copy()
            salidas['cantidad'] = salidas['cantidad'].abs()
            
            if not salidas.empty:
                g1 = salidas.groupby('producto_nombre')['cantidad'].sum().nlargest(10).reset_index()
                st.plotly_chart(px.bar(g1, x='cantidad', y='producto_nombre', orientation='h', title="Top 10 Salidas"), use_container_width=True)

elif opcion == "Users":
    st.markdown("## 👥 Configuración")
    t1, t2, t3 = st.tabs(["Usuarios", "Técnicos", "Locales"])
    
    with t1:
        with st.form("u"):
            u = st.text_input("Usuario")
            p = st.text_input("Clave")
            r = st.selectbox("Rol", ["Normal", "Super"])
            if st.form_submit_button("Crear Usuario"):
                supabase.table("usuarios").insert({"usuario":u, "contrasena":p, "rol":r}).execute()
                st.success("Creado")
    
    with t2:
        with st.form("t"):
            tn = st.text_input("Nombre Técnico")
            if st.form_submit_button("Agregar"):
                supabase.table("tecnicos").insert({"nombre":tn}).execute()
                st.rerun()
        
        ts = supabase.table("tecnicos").select("*").execute().data
        for t in ts:
            c1, c2 = st.columns([4,1])
            c1.write(t['nombre'])
            if c2.button("🗑️", key=f"dt_{t['id']}"): modal_borrar_tecnico(t['nombre'])

    with t3:
        with st.form("l"):
            ln = st.text_input("Nombre Local")
            if st.form_submit_button("Agregar"):
                supabase.table("locales").insert({"nombre":ln}).execute()
                st.rerun()
        
        ls = supabase.table("locales").select("*").execute().data
        for l in ls:
            c1, c2 = st.columns([4,1])
            c1.write(l['nombre'])
            if c2.button("🗑️", key=f"dl_{l['id']}"): modal_borrar_local(l['nombre'])

elif opcion == "Prov":
    st.markdown("## 📞 Proveedores")
    provs = supabase.table("proveedores").select("*").execute().data
    if provs:
        for p in provs:
            with st.container(border=True):
                st.write(f"**{p['nombre_contacto']}**")
                st.caption(f"Empresa: {p.get('empresa','')}")
                st.link_button("WhatsApp", f"https://wa.me/{pr['whatsapp']}")
