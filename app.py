import streamlit as st
from supabase import create_client

# Configuración Inicial
st.set_page_config(page_title="CORE SYSTEM", page_icon="⚡", layout="wide")

# Conexión
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- ESTILO CYBER-INDUSTRIAL (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;500&display=swap');
    
    * { font-family: 'JetBrains Mono', monospace; }
    .stApp { background-color: #050505; color: #00FF95; }
    
    /* Tarjetas de Producto Estilo Cristal */
    .stElementContainer div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 255, 149, 0.2) !important;
        border-radius: 4px !important;
        transition: 0.4s;
    }
    .stElementContainer div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #00FF95 !important;
        box-shadow: 0 0 20px rgba(0, 255, 149, 0.1);
    }
    
    /* Botones de Navegación Minimalistas */
    .stButton>button {
        background: transparent;
        color: #777;
        border: 1px solid #333;
        text-align: left;
        font-size: 12px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        color: #00FF95;
        border-color: #00FF95;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN LATERAL (ESTILO TERMINAL) ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF95; letter-spacing:5px;'>CORE_V2</h2>", unsafe_allow_html=True)
    st.caption("STATUS: ENCRIPTADO // ACCESO ADMIN")
    st.markdown("---")
    menu = st.radio("SISTEMA", ["01_ALMACEN", "02_PROVEEDORES", "03_LOGS", "04_CARGA"])

# --- 01_ALMACEN (INVENTARIO) ---
if menu == "01_ALMACEN":
    st.title("// CONTROL_DE_RECURSOS")
    
    col_bus, col_cat = st.columns([3, 1])
    
    with col_cat:
        st.write("CATEGORIAS_")
        for c in ["PANTALLAS", "BATERIAS", "FLEX", "GLASES"]:
            if st.button(f"> {c}", use_container_width=True): st.session_state.filtro = c.capitalize()
        if st.button("> VER_TODO", use_container_width=True): st.session_state.filtro = None

    with col_bus:
        search = st.text_input("_BUSQUEDA_RAPIDA", placeholder="Escriba ID o Modelo...")
        
        filtro = st.session_state.get('filtro')
        query = supabase.table("productos").select("*")
        if filtro: query = query.eq("categoria", filtro)
        
        items = query.execute().data
        for i in items:
            if search.lower() in i['nombre'].lower():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 1, 1])
                    c1.markdown(f"**ID_{i['id']}** // {i['nombre'].upper()}")
                    
                    val_color = "#00FF95" if i['stock'] > 3 else "#FF0055"
                    c2.markdown(f"<span style='color:{val_color}'>STOCK_{i['stock']}</span>", unsafe_allow_html=True)
                    
                    if c3.button("EJECUTAR_SALIDA", key=f"s_{i['id']}"):
                        if i['stock'] > 0:
                            supabase.table("productos").update({"stock": i['stock']-1}).eq("id", i['id']).execute()
                            supabase.table("historial").insert({"producto_nombre": i['nombre'], "cantidad": -1}).execute()
                            st.rerun()

# --- 02_PROVEEDORES (NUEVO APARTADO) ---
elif menu == "02_PROVEEDORES":
    st.title("// RED_DE_SUMINISTROS")
    
    with st.expander("+ REGISTRAR_NUEVO_CONTACTO"):
        with st.form("prov_form"):
            nombre = st.text_input("NOMBRE_CONTACTO")
            empresa = st.text_input("EMPRESA")
            wa = st.text_input("WHATSAPP (Sin espacios)")
            if st.form_submit_button("AÑADIR_A_LA_RED"):
                supabase.table("proveedores").insert({"nombre_contacto": nombre, "empresa": empresa, "whatsapp": wa}).execute()
                st.success("CONTACTO ENCRIPTADO")

    provs = supabase.table("proveedores").select("*").execute().data
    for p in provs:
        with st.container(border=True):
            col_a, col_b = st.columns([3, 1])
            col_a.write(f"CONTACTO: {p['nombre_contacto']} // EMPRESA: {p['empresa']}")
            # Botón directo para abrir WhatsApp
            url_wa = f"https://wa.me/{p['whatsapp']}"
            col_b.link_button("CONTACTAR_WA", url_wa)

# (El código de LOGS y CARGA se adapta visualmente igual)
