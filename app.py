import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ---- CONFIGURACIÓN DE PÁGINA ----
st.set_page_config(page_title="Lectura de Google Sheets", layout="centered")
st.title("📄 Lectura de los primeros 10 registros")

# ---- PARÁMETROS ----
SHEET_ID = "11--jD47K72s9ddt727kYd9BhRmAOM7qXEUB60SX69UA"
NOMBRE_HOJA = "Postulaciones"

# ---- AUTORIZACIÓN CON SECRETOS ----
scope = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_info(st.secrets["google_credentials"], scopes=scope)
gc = gspread.authorize(creds)

# ---- CARGA DE DATOS ----
sheet = gc.open_by_key(SHEET_ID).worksheet(NOMBRE_HOJA)
df = pd.DataFrame(sheet.get_all_records())

# ---- MOSTRAR PRIMEROS 10 REGISTROS ----
st.dataframe(df.head(10))


# Leer los datos
hoja = cliente.open_by_key(SHEET_ID)
datos = hoja.worksheet(NOMBRE_HOJA).get(RANGO)

# Convertir a DataFrame
if datos:
    df = pd.DataFrame(datos[1:], columns=datos[0])
    st.dataframe(df)
else:
    st.warning("No se encontraron datos.")
