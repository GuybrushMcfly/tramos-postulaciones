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
creds = Credentials.from_service_account_info(
    st.secrets["google_credentials"], scopes=scope
)
gc = gspread.authorize(creds)

# ---- CARGA DE DATOS ----
try:
    worksheet = gc.open_by_key(SHEET_ID).worksheet(NOMBRE_HOJA)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    if not df.empty:
        st.dataframe(df.head(10))
    else:
        st.warning("La hoja está vacía.")

except Exception as e:
    st.error(f"Ocurrió un error al acceder a la hoja de cálculo: {e}")
