import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, date
import time

# ==============================================================================
# 1. CONFIGURACIÓN GENERAL (SIDEBAR FIJO)
# ==============================================================================
st.set_page_config(
    page_title="VillaFix | Admin",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except:
    st.error("⚠️ Error crítico de conexión. Verifica tus 'secrets' en Streamlit.")
    st.stop()

# ==============================================================================
# 2. CSS FINAL – SIDEBAR BLOQUEADO + FLECHA ELIMINADA
# ==============================================================================
st.markdown("""
<style>

/* --- ELIMINAR CONTROLES DE COLAPSO --- */
button[aria-label="Collapse sidebar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }

/* --- SIDEBAR TOTALMENTE FIJO --- */
[data-testid="stSidebar"] {
    min-width: 300px !important;
    max-width: 300px !important;
    width: 300px !important;
    background-color: #1a222b !important;
}
section[data-testid="stMain"] {
    margin-left: 300px !important;
}

/* --- LIMPIEZA UI STREAMLIT --- */
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
header { background: transparent !important; }
footer { display: none !important; }

/* --- COLORES Y TEXTO --- */
[data-testid="stSidebar"] * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* --- BOTONES SIDEBAR --- */
[data-testid="stSidebar"] button {
    background-color: transparent !important;
    border: none !important;
    color: #bdc3c7 !important;
    text-align: left !important;
    padding-left: 15px !important;
    transition: 0.3s;
    display: block !important;
}
[data-testid="stSidebar"] button:hover {
    background-color: rgba(255,255,255,0.05) !important;
    border-left: 4px solid #3498db !important;
    color: #ffffff !important;
    padding-left: 25px !important;
}

/* --- PERFIL --- */
.profile-section { text-align: center; padding: 20px 0; }
.profile-pic {
    width: 100px; height: 100px;
    border-radius: 50%;
    border: 3px solid #f39c12;
    object-fit: cover;
    margin-bottom: 10px;
}

/* --- OCULTAR NAV NATIVO --- */
[data-testid="stSidebarNav"] { display: none; }

</style>
""", unsafe_allow_html=True)

# --- BLOQUEO JS (ANTI COLAPSO) ---
st.markdown("""
<script>
document.addEventListener("keydown", function(e) {
    if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
        e.stopPropagation();
    }
});
</script>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. SESIÓN
# ==============================================================================
SESSION_DURATION = 12 * 3600

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.user = None
    st.session_state.rol = None
    st.session_state.menu = "Stock"
    st.session_state.login_time = 0

if not st.session_state.autenticado:
    params = st.query_params
    if "user_session" in params:
        u = params["user_session"]
        r = supabase.table("usuarios").select("*").eq("usuario", u).execute()
        if r.data:
            st.session_state.autenticado = True
            st.session_state.user = u
            st.session_state.rol = r.data[0]["rol"]
            st.session_state.login_time = time.time()
            st.rerun()

if st.session_state.autenticado:
    if time.time() - st.session_state.login_time > SESSION_DURATION:
        st.session_state.autenticado = False
        st.query_params.clear()
        st.rerun()

# ==============================================================================
# 4. LOGIN
# ==============================================================================
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align:center;color:#2488bc'>VILLAFIX SYSTEM</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1.5,1])
    with c2:
        with st.container(border=True):
            with st.form("login"):
                u = st.text_input("Usuario")
                p = st.text_input("Contraseña", type="password")
                if st.form_submit_button("INGRESAR"):
                    r = supabase.table("usuarios").select("*").eq("usuario",u).eq("contrasena",p).execute()
                    if r.data:
                        st.session_state.autenticado = True
                        st.session_state.user = u
                        st.session_state.rol = r.data[0]["rol"]
                        st.session_state.login_time = time.time()
                        st.query_params["user_session"] = u
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas")
    st.stop()

# ==============================================================================
# 5. SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown(f"""
    <div class="profile-section">
        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" class="profile-pic">
        <p style="font-weight:bold">{st.session_state.user.upper()}</p>
        <p style="font-size:12px;color:#f39c12">{st.session_state.rol.upper()} USER</p>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    if st.button("📊 Dashboard / Stock"): st.session_state.menu = "Stock"
    if st.session_state.rol == "Super":
        if st.button("📥 Añadir Producto"): st.session_state.menu = "Carga"
        if st.button("📋 Historial"): st.session_state.menu = "Log"
        if st.button("📈 Estadísticas"): st.session_state.menu = "Stats"
        if st.button("👥 Usuarios / Config"): st.session_state.menu = "Users"
        if st.button("📞 Proveedores"): st.session_state.menu = "Prov"

    st.markdown("<br>")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.query_params.clear()
        st.rerun()

# ==============================================================================
# 6. CONTENIDO (NO SE TOCÓ TU LÓGICA)
# ==============================================================================
st.markdown(f"<h2>{st.session_state.menu}</h2>", unsafe_allow_html=True)
