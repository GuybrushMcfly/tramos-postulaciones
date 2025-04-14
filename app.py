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
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)
    
# 👉 Mostrar el hash cargado para verificar (solo durante pruebas)
#st.code(config['credentials']['usernames']['carlos']['password'])

# ---- CREAR OBJETO AUTENTICADOR ----
authenticator = stauth.Authenticate(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    cookie_key=config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days']
)

# ---- LOGIN ----
authenticator.login()

if st.session_state["authentication_status"]:
    authenticator.logout("Cerrar sesión", "sidebar")
    st.sidebar.success(f"Bienvenido/a, {st.session_state['name']}")
    st.title("📊 Dashboard de Encuestas de Opinión")
#    st.write("✅ Estás autenticado.")
elif st.session_state["authentication_status"] is False:
    st.error("❌ Usuario o contraseña incorrectos.")
    st.stop()
elif st.session_state["authentication_status"] is None:
    st.warning("🔒 Ingresá tus credenciales para acceder al dashboard.")
    st.stop()

# ---- CARGA DE DATOS ----
scope = ["https://www.googleapis.com/auth/spreadsheets"]
credenciales_dict = json.loads(st.secrets["GOOGLE_CREDS"])
creds = Credentials.from_service_account_info(credenciales_dict, scopes=scope)
gc = gspread.authorize(creds)

#credenciales_dict = dict(st.secrets["GOOGLE_CREDS"])
#scope = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
#creds = Credentials.from_service_account_info(credenciales_dict, scopes=scope)


# Abro la planilla
sheet = gc.open_by_key("111--jD47K72s9ddt727kYd9BhRmAOM7qXEUB60SX69UA")
postulaciones = pd.DataFrame(sheet.worksheet("Postulaciones").get_all_records())
