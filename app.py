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

import streamlit as st
import pandas as pd

# Cargar datos desde la hoja
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# --- LÓGICA DE VALORES ---
estados_validos = ["Presentada", "En Actividad Valoración", "En Actividad Capacitación"]

valor_col1 = df[df["Estado"].isin(estados_validos)]["Agente"].count()

valor_col2 = df[
    (df["Estado"].isin(estados_validos)) &
    (df["Ingresante"] == "")
]["Agente"].count()

valor_col3 = df[
    (df["Estado"].isin(estados_validos)) &
    (df["Ingresante"] == "SI")
]["Agente"].count()

valor_col4 = 0  # MONTO ESTIMADO

valor_col5 = df[df["Estado"] == "Presentada"]["Agente"].count()
valor_col6 = df[df["Estado"] == "En Actividad Capacitación"]["Agente"].count()
valor_col7 = df[df["Estado"] == "En Actividad Valoración"]["Agente"].count()
valor_col8 = 0  # APROBADAS

# --- FUNCIÓN CON CONTADOR ANIMADO ---
# Estados válidos para total postulaciones e históricos
estados_validos = ["Presentada", "En Actividad Valoración", "En Actividad Capacitación"]

# Valores reales según lógica
valor_col1 = df[df["Estado"].isin(estados_validos)]["Agente"].count()

valor_col2 = df[
    (df["Estado"].isin(estados_validos)) &
    (df["Ingresante"] == "")
]["Agente"].count()

valor_col3 = df[
    (df["Estado"].isin(estados_validos)) &
    (df["Ingresante"] == "SI")
]["Agente"].count()

valor_col4 = 0  # MONTO ESTIMADO

valor_col5 = df[df["Estado"] == "Presentada"]["Agente"].count()
valor_col6 = df[df["Estado"] == "En Actividad Capacitación"]["Agente"].count()
valor_col7 = df[df["Estado"] == "En Actividad Valoración"]["Agente"].count()
valor_col8 = 0  # APROBADAS

# Función para tarjeta con gradiente
def tarjeta_gradiente_simple(titulo, valor, gradiente):
    st.markdown(f"""
        <div style="
            background: {gradiente};
            padding: 25px;
            border-radius: 15px;
            height: 120px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.25);
            margin-bottom: 25px;
        ">
            <div style="font-size: 20px; color: white; font-weight: 700;">{titulo}</div>
            <div style="font-size: 42px; color: white; font-weight: bold;">{valor}</div>
        </div>
    """, unsafe_allow_html=True)

# Layout fila 1
col1, col2, col3, col4 = st.columns(4)

with col1:
    tarjeta_gradiente_simple("TOTAL POSTULACIONES", valor_col1, "linear-gradient(135deg, #00B4DB, #0083B0)")

with col2:
    tarjeta_gradiente_simple("POSTULACIONES HISTÓRICOS", valor_col2, "linear-gradient(135deg, #FF5858, #FB5895)")

with col3:
    tarjeta_gradiente_simple("POSTULACIONES INGRESANTES", valor_col3, "linear-gradient(135deg, #FDC830, #F37335)")

with col4:
    tarjeta_gradiente_simple("MONTO ESTIMADO", valor_col4, "linear-gradient(135deg, #C33764, #1D2671)")

# Layout fila 2
col5, col6, col7, col8 = st.columns(4)

with col5:
    tarjeta_gradiente_simple("PRESENTADAS", valor_col5, "linear-gradient(135deg, #00F260, #0575E6)")

with col6:
    tarjeta_gradiente_simple("EN ACTIVIDAD CAPACITACION", valor_col6, "linear-gradient(135deg, #7F00FF, #E100FF)")

with col7:
    tarjeta_gradiente_simple("EN ACTIVIDAD VALORACION", valor_col7, "linear-gradient(135deg, #FFE000, #799F0C)")

with col8:
    tarjeta_gradiente_simple("APROBADAS", valor_col8, "linear-gradient(135deg, #43C6AC, #191654)")



