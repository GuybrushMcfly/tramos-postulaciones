import json
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from streamlit_echarts import st_echarts
#import seaborn as sns

# ---- CONFIGURACIÓN DE PÁGINA ----
st.set_page_config(page_title="Dashboard de Tramos", layout="wide")
st.sidebar.image("logo-cap.png", use_container_width=True)

modo = st.get_option("theme.base")
color_texto = "#000000" if modo == "light" else "#FFFFFF"

# ---- CARGAR CONFIGURACIÓN DESDE YAML ----
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# ---- AUTENTICACIÓN ----
authenticator = stauth.Authenticate(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    cookie_key=config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days']
)

authenticator.login()

if st.session_state["authentication_status"]:
    authenticator.logout("Cerrar sesión", "sidebar")
    st.sidebar.success(f"Hola, {st.session_state['name']}")
    st.title("📊 Dashboard Tramos Escalafonarios")
elif st.session_state["authentication_status"] is False:
    st.error("❌ Usuario o contraseña incorrectos.")
    st.stop()
elif st.session_state["authentication_status"] is None:
    st.warning("🔒 Ingresá tus credenciales para acceder al dashboard.")
    st.stop()

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# ---- CARGA DE DATOS DE GOOGLE SHEETS ----

# 1️⃣ Definir permisos de acceso
scope = ["https://www.googleapis.com/auth/spreadsheets"]
credenciales_dict = json.loads(st.secrets["GOOGLE_CREDS"])
creds = Credentials.from_service_account_info(credenciales_dict, scopes=scope)
gc = gspread.authorize(creds)

# 2️⃣ Abrir archivo de Sheets
sheet = gc.open_by_key("11--jD47K72s9ddt727kYd9BhRmAOM7qXEUB60SX69UA")

# 3️⃣ Cargar hoja principal
worksheet = sheet.sheet1
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Cargar hoja 'valores' directamente
valores = pd.DataFrame(sheet.worksheet("valores").get_all_records())

# ---- FILTROS EN LA BARRA LATERAL ----
st.sidebar.header("Filtros")

# Filtro por Tramo
st.sidebar.subheader("TRAMO")
tramos = df["Tramo Post."].dropna()
tramos = tramos[tramos != ""].unique()
tramo_seleccionado = st.sidebar.multiselect(
    "Seleccionar uno o más tramos",
    options=sorted(tramos),
    default=sorted(tramos)
)

# Filtro por Periodo
st.sidebar.subheader("PERIODO")
periodos = df["Periodo Valoración"].dropna()
periodos = periodos[periodos != ""].unique()
periodo_seleccionado = st.sidebar.multiselect(
    "Seleccionar uno o más periodos",
    options=sorted(periodos),
    default=sorted(periodos)
)

# Filtro por Nivel Escalafonario
st.sidebar.subheader("NIVEL ESCALAFONARIO")
niveles = df["Nivel Post."].dropna()
niveles = niveles[niveles != ""].unique()
nivel_seleccionado = st.sidebar.multiselect(
    "Seleccionar uno o más niveles",
    options=sorted(niveles),
    default=sorted(niveles)
)


# Filtro por tipo de personal
df["Tipo Personal"] = df["Ingresante"].apply(lambda x: "INGRESANTES" if x == "SI" else "HISTÓRICOS")
st.sidebar.subheader("PERSONAL")
tipos_personal = df["Tipo Personal"].dropna().unique()
tipo_seleccionado = st.sidebar.multiselect(
    "Seleccionar tipo de personal",
    options=sorted(tipos_personal),
    default=sorted(tipos_personal)
)

# Aplicar filtros
df = df[
    df["Tipo Personal"].isin(tipo_seleccionado) &
    df["Tramo Post."].isin(tramo_seleccionado) &
    df["Periodo Valoración"].isin(periodo_seleccionado) &
    df["Nivel Post."].isin(nivel_seleccionado) &
    ~df["Estado"].isin(["Pendiente", "Anulada"])
]

# Agrupar tipo de comité en categorías personalizadas
df["Tipo Comité - Agrupado"] = df["Tipo Comité"].apply(lambda x: x if x in [
    "Jurisdiccional (INDEC)",
    "Transversal (INAP)",
    "Funciones informáticas (ONTI)"
] else "Otros (EXTERNOS)")



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

# --- LÓGICA DE VALORES ---
#valor_col4 = valores["Monto"].sum()
#valor_col4_mostrado = f"{valor_col4:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Asegurar que los CUIL estén como texto
valores["CUIL"] = valores["CUIL"].astype(str)
df["CUIL"] = df["CUIL"].astype(str)
# Filtrar los montos según los CUIL del df filtrado
valores_filtrados = valores[valores["CUIL"].isin(df["CUIL"])]
# Sumar y formatear
valor_col4 = valores_filtrados["Monto"].sum()
valor_col4_mostrado = f"{valor_col4:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


valor_col5 = df[df["Estado"] == "Presentada"]["Agente"].count()
valor_col6 = df[df["Estado"] == "En Actividad Capacitación"]["Agente"].count()
valor_col7 = df[df["Estado"] == "En Actividad Valoración"]["Agente"].count()
valor_col8 = 0  # APROBADAS


st.markdown("""
    <style>
    .tarjeta-hover {
        background: linear-gradient(135deg, #00B4DB, #0083B0);
        padding: 25px;
        border-radius: 15px;
        height: 120px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.25);
        margin-bottom: 25px;
        transition: all 0.3s ease;
        position: relative;
    }

    .tarjeta-hover:hover {
        transform: translateY(-5px);
        box-shadow: 0px 8px 20px rgba(0,0,0,0.35);
        cursor: default;
    }

    .tooltip-info {
        font-size: 16px;
        color: #eeeeee;
        margin-top: 8px;
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .tarjeta-hover:hover .tooltip-info {
        opacity: 1;
    }
    </style>
""", unsafe_allow_html=True)




# --- FUNCIÓN PARA TARJETAS CON GRADIENTE ---
def tarjeta_gradiente_simple(titulo, valor, gradiente):
    modo = st.get_option("theme.base") or "light"
    color_texto = "#000000" if modo == "light" else "#FFFFFF"
    sombra_texto = "1px 1px 3px #444" if modo == "dark" else "none"

    st.markdown(f"""
        <div style="
            background: {gradiente};
            padding: 25px;
            border-radius: 15px;
            height: 120px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.25);
            margin-bottom: 25px;
        ">
            <div style="font-size: 19px; color: {color_texto}; font-weight: 700; text-shadow: {sombra_texto};">
                {titulo}
            </div>
            <div style="font-size: 37px; color: {color_texto}; font-weight: bold; text-shadow: {sombra_texto};">
                {valor}
            </div>
        </div>
    """, unsafe_allow_html=True)


# --- FILA 1 ---
st.markdown("#### 🧍‍♂️🧍‍♀️ Postulaciones Totales")
col1, col2, col3, col4 = st.columns(4)

with col1:
  #  tarjeta_gradiente_simple("POSTULACIONES", valor_col1, "linear-gradient(135deg, #00B4DB, #0083B0)")
    st.markdown(f"""
    <div class="tarjeta-hover">
        <div style="font-size: 19px; color: white; font-weight: 700;">
            POSTULACIONES
        </div>
        <div style="font-size: 37px; color: white; font-weight: bold;">
            {valor_col1}
        </div>
        <div class="tooltip-info">
            Incluye postulaciones en estado activo, capacitación o valoración.
        </div>
    </div>
""", unsafe_allow_html=True)


with col2:
    tarjeta_gradiente_simple("POST. HISTÓRICOS", valor_col2, "linear-gradient(135deg, #FF5858, #FB5895)")

with col3:
    tarjeta_gradiente_simple("POST. INGRESANTES", valor_col3, "linear-gradient(135deg, #FDC830, #F37335)")

with col4:
    tarjeta_gradiente_simple("MONTO ESTIMADO", valor_col4_mostrado, "linear-gradient(135deg, #C33764, #1D2671)")

# --- FILA 2 ---
st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

st.markdown("#### 📂 Estado de Tramitaciones")
col5, col6, col7, col8 = st.columns(4)

with col5:
    tarjeta_gradiente_simple("PRESENTADAS", valor_col5, "linear-gradient(135deg, #00F260, #0575E6)")

with col6:
    tarjeta_gradiente_simple("EN ACTIV. CAPACITACION", valor_col6, "linear-gradient(135deg, #7F00FF, #E100FF)")

with col7:
    tarjeta_gradiente_simple("EN ACTIV. VALORACION", valor_col7, "linear-gradient(135deg, #43e97b, #38f9d7)")

with col8:
    tarjeta_gradiente_simple("APROBADAS", valor_col8, "linear-gradient(135deg, #43C6AC, #191654)")


st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

# --- FUNCIÓN PARA GRÁFICOS PIE ---
def pie_chart_donut(df, columna, titulo, key_id):
    conteo = df[columna].value_counts().reset_index()
    conteo.columns = ["name", "value"]
    data = conteo.to_dict(orient="records")

    # Detectar tema y color de texto
    modo = st.get_option("theme.base") or "light"
    color_texto = "#000000" if modo == "light" else "#CCCCCC"

    option = {
        "title": {
            "text": titulo,
            "left": "center",
            "top": "top",
            "textStyle": {
                "fontSize": 16,
                "fontWeight": "bold",
                "color": color_texto
            }
        },  # ← esta llave FALTABA
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}: {c} ({d}%)"
        },
        "legend": {
            "orient": "horizontal",
            "top": "90%",  # más arriba para que no se corte
            "left": "center",
            "padding": [0, 0, 20, 0],
            "textStyle": {"color": color_texto}
        },
        
        "series": [
            {
                "name": titulo,
                "type": "pie",
                "radius": ["40%", "75%"],
                "avoidLabelOverlap": False,
                "itemStyle": {
                    "borderRadius": 10,
                    "borderColor": "#fff",
                    "borderWidth": 2
                },
                "label": {
                    "show": False,
                    "position": "center",
                    "color": color_texto
                },
                "emphasis": {
                    "label": {
                        "show": True,
                        "fontSize": 20,
                        "fontWeight": "bold",
                        "color": color_texto
                    }
                },
                "labelLine": {
                    "show": True,
                    "lineStyle": {"color": color_texto}
                },
                "data": data
            }
        ]
    }

    st_echarts(options=option, height="380px", key=key_id)



# --- GRILLA 3x3 DE PIE CHARTS ---

# FILA 1
col1, col2, col3 = st.columns(3)

with col1:
    pie_chart_donut(df, "Puesto Tipo", "Distribución por Puesto Tipo", "pie1")

with col2:
    pie_chart_donut(df, "Tipo Comité - Agrupado", "Distribución por Tipo Comité", "pie2")

with col3:
    pie_chart_donut(df, "Nivel Post.", "Distribución por Nivel", "pie3")

st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

# FILA 2
col4, col5, col6 = st.columns(3)

with col4:
    pie_chart_donut(df, "Modalidad", "Distribución por Modalidad", "pie4")

with col5:
    pie_chart_donut(df, "Tramo Post.", "Distribución por Tramo", "pie5")

with col6:
    pie_chart_donut(df, "Agrup. Post.", "Distribución por Agrupamiento", "pie6")


#----------------------
st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)

# Obtener las columnas de la hoja "tabla-dash"
postulaciones = pd.DataFrame(sheet.worksheet("tabla-dash").get_all_records())
columnas_tabla_dash = postulaciones.columns.tolist()

# Aplicar esas columnas al df filtrado (descartando cualquier otra)
df_filtrado_para_mostrar = df.copy()
df_filtrado_para_mostrar = df_filtrado_para_mostrar[[col for col in columnas_tabla_dash if col in df_filtrado_para_mostrar.columns]]

# Mostrar con expander
st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)

with st.expander("🔍 #### VER POSTULACIONES FILTRADAS 🔎"):
    st.dataframe(df_filtrado_para_mostrar, use_container_width=True, hide_index=True)


# ----------------------
# ----------------------
st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
st.markdown("##### 📊 Personas por Dependencia Nacional y Nivel Escalafonario")

# Cargar hoja "tabla-dash"
tabla_dash = pd.DataFrame(sheet.worksheet("tabla-dash").get_all_records())

# Renombrar columna para mostrar
tabla_dash["DEPENDENCIA NACIONAL/GENERAL"] = tabla_dash["Dep. Nacional"]

# Asegurar tipos correctos
tabla_dash["Nivel Post."] = tabla_dash["Nivel Post."].astype(str)
tabla_dash["DEPENDENCIA NACIONAL/GENERAL"] = tabla_dash["DEPENDENCIA NACIONAL/GENERAL"].astype(str)

# Crear tabla dinámica para gráfico
tabla_dinamica = tabla_dash.pivot_table(
    index="DEPENDENCIA NACIONAL/GENERAL",
    columns="Nivel Post.",
    values="Agente",
    aggfunc="count",
    fill_value=0
).reset_index()

# Preparar datos para gráfico de barras apilado 100%
df_grafico = tabla_dinamica.set_index("DEPENDENCIA NACIONAL/GENERAL")
df_totales = df_grafico.sum(axis=1)
df_porcentajes = df_grafico.div(df_totales, axis=0) * 100
df_porcentajes = df_porcentajes.fillna(0)

# Convertir a formato largo
df_melt_abs = df_grafico.reset_index().melt(id_vars="DEPENDENCIA NACIONAL/GENERAL", var_name="Nivel", value_name="Absoluto")
df_melt_pct = df_porcentajes.reset_index().melt(id_vars="DEPENDENCIA NACIONAL/GENERAL", var_name="Nivel", value_name="Porcentaje")
df_graf_final = df_melt_abs.merge(df_melt_pct, on=["DEPENDENCIA NACIONAL/GENERAL", "Nivel"])

# Colores personalizados definitivos
colores_custom = ["#0c555c", "#007f5b", "#7b9f28", "#ffa600"]

# Crear gráfico
import plotly.graph_objects as go

fig = go.Figure()
niveles = sorted(df_graf_final["Nivel"].unique())  # ordenamos los niveles si querés A-B-C-D

for i, nivel in enumerate(niveles):
    datos_nivel = df_graf_final[df_graf_final["Nivel"] == nivel]
    fig.add_trace(go.Bar(
        y=datos_nivel["DEPENDENCIA NACIONAL/GENERAL"],
        x=datos_nivel["Porcentaje"],
        name=nivel,
        orientation="h",
        marker=dict(color=colores_custom[i % len(colores_custom)]),
        hovertemplate=(
            "<b>%{y}</b><br>" +
            "Nivel: <b>" + nivel + "</b><br>" +
            "Cantidad: %{customdata[0]}<br>" +
            "Porcentaje: %{x:.1f}%<extra></extra>"
        ),
        customdata=datos_nivel[["Absoluto"]]
    ))

# Configuración del layout
fig.update_layout(
    barmode="stack",
    xaxis=dict(title="Porcentaje", range=[0, 100], ticksuffix="%"),
    yaxis=dict(title=""),
    legend_title="Nivel Escalafonario",
    height=700,
    margin=dict(t=40, b=40, l=40, r=10),
    plot_bgcolor="rgba(0,0,0,0)"
)

# Mostrar gráfico en Streamlit
st.plotly_chart(fig, use_container_width=True)




# --- TABLA DINÁMICA DE MONTOS POR MES Y NIVEL ---

# Asegurar formato correcto
valores["Periodo"] = pd.to_datetime(valores["Periodo Valoracion"].astype(str) + "01", format="%Y%m%d", errors="coerce")
valores["CUIL"] = valores["CUIL"].astype(str)
valores["Nivel"] = valores["Nivel Post."].astype(str)
valores["Monto"] = (
    valores["Monto"].astype(str)
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
)
valores["Monto"] = pd.to_numeric(valores["Monto"], errors="coerce").fillna(0)

# Diccionario de meses en español
meses_es = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}

# Crear columna "Mes" con formato mes-año
valores["Periodo_Orden"] = valores["Periodo"]
valores["Mes"] = valores["Periodo"].dt.month.map(meses_es) + "-" + valores["Periodo"].dt.strftime("%y")

# Tabla dinámica
pivot_valores = valores.pivot_table(
    index=["Periodo_Orden", "Mes"],
    columns="Nivel",
    values="Monto",
    aggfunc="sum",
    fill_value=0
).reset_index().sort_values("Periodo_Orden")

# Limpiar columnas auxiliares
pivot_valores = pivot_valores.drop(columns=["Periodo_Orden"])
pivot_valores = pivot_valores.reset_index(drop=True)

# Asegurar que existan todas las columnas A, B, C, D
for nivel in ["A", "B", "C", "D"]:
    if nivel not in pivot_valores.columns:
        pivot_valores[nivel] = 0

# Calcular total
pivot_valores["Total"] = pivot_valores[["A", "B", "C", "D"]].sum(axis=1)

# Reordenar columnas
columnas_finales = ["Mes", "A", "B", "C", "D", "Total"]
pivot_valores = pivot_valores[columnas_finales]

# Mostrar tabla en el dashboard
st.markdown("### 📊 Tabla dinámica de montos por Nivel y Mes")
st.dataframe(pivot_valores, use_container_width=True, hide_index=True)



