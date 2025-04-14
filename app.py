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

# Layout de las tarjetas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("TOTAL AGENTES", total_agentes)

with col2:
    st.metric("TOTAL AGENTES", total_agentes)

with col3:
    st.metric("TOTAL AGENTES", total_agentes)

with col4:
    st.metric("TOTAL AGENTES", total_agentes)


# Leer datos desde la hoja (ya tenés conexión con gspread)
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Contar agentes
total_agentes = df["Agente"].count()

# Layout de las tarjetas
col1, col2, col3, col4 = st.columns(4)

# Estilo de cada tarjeta
def tarjeta(titulo, valor, color, icono):
    st.markdown(f"""
        <div style="background-color:{color}; padding:20px; border-radius:10px; text-align:left; height:140px; position:relative;">
            <div style="font-size:14px; color:white; font-weight:bold;">{titulo}</div>
            <div style="font-size:32px; color:white; font-weight:bold;">{valor}</div>
            <div style="font-size:12px; color:white;">Monthly progress</div>
            <div style="position:absolute; top:10px; right:10px; font-size:32px;">{icono}</div>
        </div>
    """, unsafe_allow_html=True)

with col1:
    tarjeta("TOTAL AGENTES", total_agentes, "#2196F3", "🧊")

with col2:
    tarjeta("ACTIVOS HOY", total_agentes, "#E91E63", "👥")

with col3:
    tarjeta("NUEVOS INGRESOS", total_agentes, "#FF9800", "🛒")

with col4:
    tarjeta("COMENTARIOS", total_agentes, "#9C27B0", "💬")


# Simulación de datos
total_agentes = 233

# Definición de tarjetas con gradientes
def tarjeta_gradiente(titulo, valor, gradiente, icono):
    st.markdown(f"""
        <div style="
            background: {gradiente};
            padding: 20px;
            border-radius: 15px;
            height: 140px;
            position: relative;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.25);
        ">
            <div style="font-size: 14px; color: white; font-weight: bold;">{titulo}</div>
            <div style="font-size: 32px; color: white; font-weight: bold;">{valor}</div>
            <div style="font-size: 12px; color: white;">Monthly progress</div>
            <div style="position: absolute; top: 10px; right: 15px; font-size: 32px; opacity: 0.5;">{icono}</div>
        </div>
    """, unsafe_allow_html=True)

# Layout en 4 columnas
col1, col2, col3, col4 = st.columns(4)

with col1:
    tarjeta_gradiente("TOTAL AGENTES", total_agentes, "linear-gradient(135deg, #36D1DC, #5B86E5)", "🧊")

with col2:
    tarjeta_gradiente("ACTIVOS HOY", total_agentes, "linear-gradient(135deg, #FF416C, #FF4B2B)", "👥")

with col3:
    tarjeta_gradiente("NUEVOS INGRESOS", total_agentes, "linear-gradient(135deg, #FDC830, #F37335)", "🛒")

with col4:
    tarjeta_gradiente("COMENTARIOS", total_agentes, "linear-gradient(135deg, #B24592, #F15F79)", "💬")
