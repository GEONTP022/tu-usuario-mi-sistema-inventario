# --- DISEÑO UI PREMIUM (ALINEACIÓN IZQUIERDA TOTAL) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; color: #1e1e2f; }
    
    /* SIDEBAR AJUSTADO A LA IZQUIERDA */
    [data-testid="stSidebar"] {
        background-color: #1a222b !important;
        color: white !important;
    }

    /* ELIMINAR PADDING INTERNO DEL SIDEBAR */
    [data-testid="stSidebarUserContent"] {
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        padding-top: 1rem !important;
    }

    /* PERFIL ALINEADO A LA IZQUIERDA */
    .profile-section {
        text-align: left; /* Alineado a la izquierda */
        padding: 10px 0px 20px 20px; /* Margen solo a la izquierda */
        background: #1a222b;
    }
    .profile-pic {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        border: 3px solid #f39c12;
        margin-bottom: 10px;
        object-fit: cover;
    }
    .profile-name { 
        font-size: 16px; 
        font-weight: bold; 
        color: white; 
        margin: 0;
        text-transform: uppercase;
    }
    .profile-status { 
        font-size: 11px; 
        color: #95a5a6; 
        margin: 0;
    }

    .sidebar-divider {
        height: 1px;
        background-color: #3498db;
        margin: 10px 0px;
        width: 100%;
        opacity: 0.5;
    }

    /* BOTONES TOTALMENTE PEGADOS A LA IZQUIERDA Y RECTOS */
    .stSidebar .stButton>button {
        background-color: transparent;
        color: #bdc3c7;
        border: none;
        border-radius: 0;
        height: 45px;
        text-align: left; /* Texto a la izquierda */
        font-size: 14px;
        width: 100%;
        padding-left: 20px !important; /* Alineación constante */
        margin: 0 !important;
        transition: 0.2s;
        display: flex;
        align-items: center;
        border-left: 0px solid #3498db;
    }
    
    .stSidebar .stButton>button:hover {
        background-color: #2c3e50 !important;
        color: white !important;
        border-left: 5px solid #3498db !important;
    }
    
    /* ICONOS Y TEXTO EN LINEA RECTA */
    .stSidebar .stButton>button div {
        text-align: left !important;
    }
    
    [data-testid="stSidebarNav"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# --- PANEL IZQUIERDO (SIDEBAR) ---
with st.sidebar:
    # Perfil alineado a la izquierda según tu solicitud
    st.markdown(f"""
        <div class="profile-section">
            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" class="profile-pic">
            <p class="profile-name">{st.session_state.user}</p>
            <p class="profile-status">{st.session_state.rol} USER</p>
        </div>
        <div class="sidebar-divider"></div>
    """, unsafe_allow_html=True)
    
    # Navegación con alineación recta y pegada a la izquierda
    if st.button("📊 Dashboard / Stock", use_container_width=True): st.session_state.menu = "Stock"
    
    if st.session_state.rol == "Super":
        if st.button("📥 Nuevo Producto", use_container_width=True): st.session_state.menu = "Carga"
        if st.button("📋 Historial", use_container_width=True): st.session_state.menu = "Log"
        if st.button("📈 Estadísticas", use_container_width=True): st.session_state.menu = "Stats"
        if st.button("👥 Usuarios", use_container_width=True): st.session_state.menu = "Users"
        if st.button("📞 Proveedores", use_container_width=True): st.session_state.menu = "Prov"

    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()
