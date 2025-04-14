import json
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# ---- CONFIGURACIÓN DE PÁGINA ----
st.set_page_config(page_title="Dashboard de Tramos", layout="wide")

# ---- CARGAR CONFIGURACIÓN DESDE YAML ----
#with open("config.yaml") as file:
#    config = yaml.load(file, Loader=SafeLoader)
    
# 👉 Mostrar el hash cargado para verificar (solo durante pruebas)
#st.code(config['credentials']['usernames']['carlos']['password'])

# ---- CREAR OBJETO AUTENTICADOR ----
#authenticator = stauth.Authenticate(
#    credentials=config['credentials'],
#    cookie_name=config['cookie']['name'],
#    cookie_key=config['cookie']['key'],
#    cookie_expiry_days=config['cookie']['expiry_days']
#)

# ---- LOGIN ----
#authenticator.login()

#if st.session_state["authentication_status"]:
#    authenticator.logout("Cerrar sesión", "sidebar")
#    st.sidebar.success(f"Bienvenido/a, {st.session_state['name']}")
#    st.title("📊 Dashboard de Encuestas de Opinión")
##    st.write("✅ Estás autenticado.")
#elif st.session_state["authentication_status"] is False:
#    st.error("❌ Usuario o contraseña incorrectos.")
#    st.stop()
#elif st.session_state["authentication_status"] is None:
#    st.warning("🔒 Ingresá tus credenciales para acceder al dashboard.")
#    st.stop()

# ---- CARGA DE DATOS ----
scope = ["https://www.googleapis.com/auth/spreadsheets"]
credenciales_dict = json.loads(st.secrets["GOOGLE_CREDS"])
creds = Credentials.from_service_account_info(credenciales_dict, scopes=scope)
gc = gspread.authorize(creds)

#credenciales_dict = dict(st.secrets["GOOGLE_CREDS"])
#scope = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
#creds = Credentials.from_service_account_info(credenciales_dict, scopes=scope)


# Abro la planilla
sheet = gc.open_by_key("11--jD47K72s9ddt727kYd9BhRmAOM7qXEUB60SX69UA")
postulaciones = pd.DataFrame(sheet.worksheet("Postulaciones").get_all_records())


worksheet = gc.open_by_key("11--jD47K72s9ddt727kYd9BhRmAOM7qXEUB60SX69UA").sheet1
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Contar agentes
total_agentes = df["Agente"].count()

# Simulación de valor para todos (cambiá por lo que corresponda)
valor = 233

# Función para tarjeta con gradiente
def tarjeta_gradiente_simple(titulo, valor, gradiente):
    st.markdown(f"""
        <div style="
            background: {gradiente};
            padding: 20px;
            border-radius: 15px;
            height: 100px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.25);
        ">
            <div style="font-size: 14px; color: white; font-weight: bold;">{titulo}</div>
            <div style="font-size: 32px; color: white; font-weight: bold;">{valor}</div>
        </div>
    """, unsafe_allow_html=True)

# Layout fila 1
col1, col2, col3, col4 = st.columns(4)

with col1:
    tarjeta_gradiente_simple("TOTAL POSTULACIONES", valor, "linear-gradient(135deg, #36D1DC, #5B86E5)")

with col2:
    tarjeta_gradiente_simple("POSTULACIONES HISTÓRICOS", valor, "linear-gradient(135deg, #FF416C, #FF4B2B)")

with col3:
    tarjeta_gradiente_simple("POSTULACIONES INGRESANTES", valor, "linear-gradient(135deg, #FDC830, #F37335)")

with col4:
    tarjeta_gradiente_simple("MONTO ESTIMADO", valor, "linear-gradient(135deg, #B24592, #F15F79)")

# Layout fila 2
col5, col6, col7, col8 = st.columns(4)

with col5:
    tarjeta_gradiente_simple("PRESENTADAS", valor, "linear-gradient(135deg, #00C9FF, #92FE9D)")

with col6:
    tarjeta_gradiente_simple("EN ACTIVIDAD CAPACITACION", valor, "linear-gradient(135deg, #667EEA, #764BA2)")

with col7:
    tarjeta_gradiente_simple("EN ACTIVIDAD VALORACION", valor, "linear-gradient(135deg, #F7971E, #FFD200)")

with col8:
    tarjeta_gradiente_simple("APROBADAS", valor, "linear-gradient(135deg, #00F260, #0575E6)")

with col3:
    tarjeta_gradiente("NUEVOS INGRESOS", total_agentes, "linear-gradient(135deg, #FDC830, #F37335)", "🛒")

with col4:
    tarjeta_gradiente("COMENTARIOS", total_agentes, "linear-gradient(135deg, #B24592, #F15F79)", "💬")
