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

# --- CSS MAESTRO (EL DISEÑO QUE TE GUSTA, PERO ESTABILIZADO) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #1a222b; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    
    /* Botones Sidebar */
    [data-testid="stSidebar"] button { background-color: transparent !important; border: none !important; color: #bdc3c7 !important; text-align: left !important; padding-left: 15px !important; }
    [data-testid="stSidebar"] button:hover { background-color: rgba(255,255,255,0.05) !important; border-left: 4px solid #3498db !important; color: #ffffff !important; }
    
    /* Textos Negros */
    div[data-testid="stWidgetLabel"] p, label, h1, h2, h3, .stDialog p, div[role="dialog"] p, .stMetricLabel { color: #000000 !important; font-weight: 700 !important; }
    div[data-testid="stMetricValue"] { color: #2488bc !important; }
    
    /* Inputs */
    input, textarea, .stNumberInput input { background-color: #ffffff !important; color: #000000 !important; border: 1px solid #888888 !important; }
    input:disabled { background-color: #e9ecef !important; }
    
    /* Tarjetas de Producto (Estilo Original Restaurado) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 1px solid #ddd !important;
        padding: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        /* IMPORTANTE: Altura mínima para que se vean iguales pero flexible */
        min-height: 380px !important; 
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    /* Imágenes Centradas */
    div[data-testid="stImage"] {
        display: flex !important;
        justify-content: center !important; 
        align-items: center !important;
        width: 100% !important;
        height: 150px !important; 
        margin-bottom: 10px;
    }
    div[data-testid="stImage"] img {
        max-height: 140px !important;
        width: auto !important;
        object-fit: contain !important;
    }

    /* Botones */
    div.stButton button { background-color: #2488bc !important; color: #ffffff !important; border: none !important; font-weight: bold !important; width: 100% !important; margin-top: auto !important; }
    div.stButton button:disabled { background-color: #e74c3c !important; color: white !important; opacity: 1 !important; border: 1px solid #c0392b !important; }
    
    [data-testid="stSidebarNav"] {display: none;}
    .profile-section { text-align: center !important; padding: 20px 0px; }
    .profile-pic { width: 100px; height: 100px; border-radius: 50%; border: 3px solid #f39c12; object-fit: cover; display: block; margin: 0 auto 10px auto; }
    </style>
    """, unsafe_allow_html=True)

# --- MODALES ---
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
        st.info("Devolución de técnico o ingreso rápido.")
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
    st.markdown("<h3 style='color:black;'>Crear Producto</h3>", unsafe_allow_html=True)
    with st.form("form_nuevo_prod"):
        n = st.text_input("Nombre / Modelo *")
        c = st.selectbox("Categoría *", ["Seleccionar", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])
        m = st.text_input("Marca (Solo si aplica)")
        cb = st.text_input("Código de Batería (Solo para Baterías)")
        s = st.number_input("Stock Inicial *", min_value=0, step=1)
        
        c1, c2 = st.columns(2)
        with c1: p_gen = st.number_input("Precio General (S/) *", min_value=0.0, step=0.5)
        with c2: p_punto = st.number_input("Precio Punto (S/)", min_value=0.0, step=0.5)
        
        img = st.text_input("URL Imagen (Opcional)")

        if st.form_submit_button("GUARDAR"):
            if not n or c == "Seleccionar" or p_gen <= 0:
                st.error("⚠️ Datos incompletos.")
            else:
                # VALIDACIÓN INTELIGENTE (TU PEDIDO):
                # Solo bloquea si Nombre + Marca + Categoría + Código son IDÉNTICOS.
                # Si cambia UNA sola cosa (ej: el código es igual pero el modelo es otro), TE DEJA PASAR.
                
                query = supabase.table("productos").select("id")\
                    .eq("nombre", n).eq("marca", m).eq("categoria", c)
                
                if cb: query = query.eq("codigo_bateria", cb)
                else: query = query.eq("codigo_bateria", "")

                existe = query.execute()

                if existe.data:
                    st.error("⚠️ Ya existe este producto EXACTO (Mismo nombre, marca y código).")
                else:
                    with st.spinner('Creando...'):
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
    st.write(f"¿Eliminar **{producto['nombre']}**?")
    if st.button("SÍ, ELIMINAR", type="primary"):
        with st.spinner('Eliminando...'):
            supabase.table("productos").delete().eq("id", producto['id']).execute()
        st.success("✅ Eliminado")
        time.sleep(0.5)
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

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# --- ÁREA CENTRAL ---
opcion = st.session_state.menu

if opcion == "Stock":
    st.markdown("<h2>Inventario General</h2>", unsafe_allow_html=True)
    col_a, col_b = st.columns([3, 1])
    with col_a: busqueda = st.text_input("Buscar...", placeholder="Ej: ip11, Samsung, celda...")
    with col_b: categoria = st.selectbox("Apartado", ["Todos", "⚠️ Solo Bajo Stock", "Pantallas", "Baterías", "Flex", "Glases", "Otros"])

    items = supabase.table("productos").select("*").order("nombre").execute().data
    if items:
        # Filtrado
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

        # --- GRID SYSTEM ROBUSTO (4 por fila) ---
        # Usamos st.columns dentro de un bucle para dibujar fila por fila.
        # Esto previene el error visual de superposición.
        columnas_por_fila = 4
        # Dividimos la lista de productos en trozos de 4
        chunks = [filtered_items[i:i + columnas_por_fila] for i in range(0, len(filtered_items), columnas_por_fila)]

        for chunk in chunks:
            cols = st.columns(columnas_por_fila)
            for i, p in enumerate(chunk):
                with cols[i]:
                    with st.container(border=True):
                        # Imagen (Protegida)
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
                            if p_punto and p_punto > 0:
                                st.markdown(f"<div style='text-align:center; color:#27ae60; font-size:12px;'>Punto<br><span style='font-weight:bold;'>S/ {p_punto}</span></div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='text-align:center; color:#bdc3c7; font-size:12px;'>Punto<br>--</div>", unsafe_allow_html=True)
                        
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
            with st.form("edit_form"):
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    new_cat = st.selectbox("Categoría", ["Pantallas", "Baterías", "Flex", "Glases", "Otros"], index=["Pantallas", "Baterías", "Flex", "Glases", "Otros"].index(prod['categoria']))
                    new_marca = st.text_input("Marca", value=prod.get('marca', ''))
                    new_cod = st.text_input("Código Batería", value=prod.get('codigo_bateria', ''))
                with col_u2:
                    new_p_gen = st.number_input("Precio Gral", value=float(prod['precio_venta']), step=0.5)
                    # Protección contra nulls en precio_punto
                    val_punto = float(prod.get('precio_punto') or 0.0)
                    new_p_punto = st.number_input("Precio Punto", value=val_punto, step=0.5)
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
    st.markdown("<h2>📜 Historial</h2>", unsafe_allow_html=True)
    today = datetime.now()
    d_range = st.date_input("Filtrar fecha:", (today - timedelta(days=30), today))
    
    logs = supabase.table("historial").select("*").order("fecha", desc=True).execute().data
    if logs:
        df = pd.DataFrame(logs)
        # FIX FECHAS: Convertir a fecha simple para filtro
        df['dt'] = pd.to_datetime(df['fecha']).dt.date
        if len(d_range) == 2:
            df = df[(df['dt'] >= d_range[0]) & (df['dt'] <= d_range[1])]
        
        # Formato legible para tabla
        df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m/%Y %H:%M')
        st.dataframe(
            df[['fecha', 'producto_nombre', 'cantidad', 'usuario', 'tecnico', 'local']], 
            use_container_width=True, 
            hide_index=True
        )

elif opcion == "Stats":
    st.markdown("<h2>📊 Estadísticas</h2>", unsafe_allow_html=True)
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
            df_h['dt'] = pd.to_datetime(df_h['fecha']).dt.date
            if len(dr) == 2:
                df_h = df_h[(df_h['dt'] >= dr[0]) & (df_h['dt'] <= dr[1])]
            
            salidas = df_h[df_h['cantidad'] < 0].copy()
            salidas['cantidad'] = salidas['cantidad'].abs()
            
            if not salidas.empty:
                g1 = salidas.groupby('producto_nombre')['cantidad'].sum().nlargest(10).reset_index()
                st.plotly_chart(px.bar(g1, x='cantidad', y='producto_nombre', orientation='h', title="Top 10 Salidas"), use_container_width=True)

elif opcion == "Users":
    st.markdown("<h2>👥 Configuración</h2>", unsafe_allow_html=True)
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
    st.markdown("<h2>📞 Proveedores</h2>", unsafe_allow_html=True)
    provs = supabase.table("proveedores").select("*").execute().data
    if provs:
        for p in provs:
            with st.container(border=True):
                st.write(f"**{p['nombre_contacto']}**")
                st.caption(f"Empresa: {p.get('empresa','')}")
                st.link_button("WhatsApp", f"https://wa.me/{pr['whatsapp']}")
