import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Lectura de Google Sheets", layout="centered")
st.title("📄 Lectura de los primeros 10 registros")

# ID de la hoja
SHEET_ID = "11--jD47K72s9ddt727kYd9BhRmAOM7qXEUB60SX69UA"
NOMBRE_HOJA = "Postulaciones"  # Cambiá esto si tu hoja se llama diferente
RANGO = "A1:M10"  # Primeros 10 registros desde la columna A

# Cargar credenciales
creds = Credentials.from_service_account_file("credenciales_google.json", scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
cliente = gspread.authorize(creds)

# Leer los datos
hoja = cliente.open_by_key(SHEET_ID)
datos = hoja.worksheet(NOMBRE_HOJA).get(RANGO)

# Convertir a DataFrame
if datos:
    df = pd.DataFrame(datos[1:], columns=datos[0])
    st.dataframe(df)
else:
    st.warning("No se encontraron datos.")
