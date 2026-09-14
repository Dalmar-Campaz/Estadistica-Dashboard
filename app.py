import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Dashboard Inmuebles CISA",
    page_icon="🏢",
    layout="wide"
)


# ============================================================
# CARGA DE DATOS
# ============================================================

@st.cache_data
def cargar_datos():
    archivo = "Inmuebles_CISA.xlsx"

    df = pd.read_excel(archivo)

    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip()

    # Eliminar espacios innecesarios en variables de texto
    columnas_texto = [
        "Ciudad",
        "Departamento",
        "Orientacion",
        "Tipo_Inmueble",
        "Estado_Inmueble"
    ]

    for columna in columnas_texto:
        if columna in df.columns:
            df[columna] = df[columna].astype(str).str.strip()

    # Asegurar que el precio sea numérico
    df["Precio_VTA_MM"] = pd.to_numeric(
        df["Precio_VTA_MM"],
        errors="coerce"
    )

    return df


# Intentar cargar los datos
try:
    df = cargar_datos()

except FileNotFoundError:
    st.error(
        "No se encontró el archivo 'Inmuebles_CISA.xlsx'. "
        "Colócalo en la misma carpeta que app.py."
    )
    st.stop()

except Exception as e:
    st.error(f"Error al cargar el archivo: {e}")
    st.stop()


# ============================================================
# VALIDACIÓN DE COLUMNAS
# ============================================================

columnas_requeridas = [
    "Codigo",
    "Ciudad",
    "Departamento",
    "Orientacion",
    "Precio_VTA_MM",
    "Tipo_Inmueble",
    "Estado_Inmueble"
]

faltantes = [
    columna
    for columna in columnas_requeridas
    if columna not in df.columns
]

if faltantes:
    st.error(
        "El archivo no contiene las siguientes columnas requeridas: "
        + ", ".join(faltantes)
    )
    st.stop()


# ============================================================
# TÍTULO
# ============================================================

st.title("🏢 Dashboard de Inmuebles CISA")

st.markdown(
    """
    **Análisis interactivo de los inmuebles disponibles para la venta.**

    Utilice el filtro del panel izquierdo para analizar la información
    de un departamento específico o consultar el total nacional.
    """
)

st.divider()


# ============================================================
# SIDEBAR - FILTRO PRINCIPAL
# ============================================================

st.sidebar.header("🔎 Filtros")

departamentos = sorted(
    df["Departamento"]
    .dropna()
    .unique()
    .tolist()
)

opciones_departamento = ["TODOS"] + departamentos

departamento_seleccionado = st.sidebar.selectbox(
    "Seleccione un departamento:",
    opciones_departamento,
    index=0
)


# ============================================================
# FILTRADO
# ============================================================

if departamento_seleccionado == "TODOS":

    df_filtrado = df.copy()

else:

    df_filtrado = df[
        df["Departamento"] == departamento_seleccionado
    ].copy()


# ============================================================
# INFORMACIÓN DEL FILTRO
# ============================================================

if departamento_seleccionado == "TODOS":

    st.info(
        f"📍 Mostrando información de **todos los departamentos** "
        f"({len(df_filtrado):,} inmuebles)."
    )

else:

    st.info(
        f"📍 Departamento seleccionado: "
        f"**{departamento_seleccionado}** — "
        f"{len(df_filtrado):,} inmuebles."
    )


# ============================================================
# KPIs
# ============================================================

total_inmuebles = len(df_filtrado)

precio_promedio = df_filtrado["Precio_VTA_MM"].mean()

precio_maximo = df_filtrado["Precio_VTA_MM"].max()

# Promedio por departamento
promedio_por_departamento = (
    df_filtrado.groupby("Departamento")["Precio_VTA_MM"]
    .mean()
    .mean()
)


# Crear columnas para los indicadores
col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        label="🏠 Total de Inmuebles",
        value=f"{total_inmuebles:,}"
    )


with col2:
    st.metric(
        label="💰 Precio Promedio",
        value=f"${precio_promedio:,.2f} MM"
        if pd.notna(precio_promedio)
        else "N/D"
    )


with col3:
    st.metric(
        label="💎 Precio Máximo",
        value=f"${precio_maximo:,.2f} MM"
        if pd.notna(precio_maximo)
        else "N/D"
    )


with col4:
    st.metric(
        label="📊 Promedio por Dep.",
        value=f"${promedio_por_departamento:,.2f} MM"
        if pd.notna(promedio_por_departamento)
        else "N/D"
    )


st.divider()


# ============================================================
# GRÁFICO 1
# DISTRIBUCIÓN DE INMUEBLES POR CIUDAD
# ============================================================

st.subheader("1️⃣ Distribución de Inmuebles por Ciudad")

datos_ciudad = (
    df_filtrado["Ciudad"]
    .value_counts()
    .reset_index()
)

datos_ciudad.columns = ["Ciudad", "Cantidad"]

datos_ciudad = datos_ciudad.sort_values(
    "Cantidad",
    ascending=True
)

fig_ciudad = px.bar(
    datos_ciudad,
    x="Cantidad",
    y="Ciudad",
    orientation="h",
    text="Cantidad",
    title="Cantidad de inmuebles por ciudad",
    labels={
        "Cantidad": "Número de inmuebles",
        "Ciudad": "Ciudad"
    }
)

fig_ciudad.update_traces(
    textposition="outside"
)

fig_ciudad.update_layout(
    height=max(400, len(datos_ciudad) * 25),
    showlegend=False,
    margin=dict(l=20, r=50, t=60, b=20)
)

st.plotly_chart(
    fig_ciudad,
    use_container_width=True
)


# ============================================================
# GRÁFICO 2
# DISTRIBUCIÓN POR ORIENTACIÓN
# ============================================================

st.subheader("2️⃣ Distribución por Orientación de Uso")

datos_orientacion = (
    df_filtrado["Orientacion"]
    .value_counts()
    .reset_index()
)

datos_orientacion.columns = [
    "Orientacion",
    "Cantidad"
]

fig_orientacion = px.pie(
    datos_orientacion,
    names="Orientacion",
    values="Cantidad",
    title="Distribución de inmuebles según orientación",
    hole=0.35
)

fig_orientacion.update_traces(
    textposition="inside",
    textinfo="percent+label"
)

st.plotly_chart(
    fig_orientacion,
    use_container_width=True
)


# ============================================================
# GRÁFICO 3
# HISTOGRAMA DE PRECIO
# MÁXIMO 12 INTERVALOS
# ============================================================

st.subheader("3️⃣ Distribución del Precio de Venta")

precios = df_filtrado["Precio_VTA_MM"].dropna()

if len(precios) > 0:

    # IMPORTANTE:
    # Se limita estrictamente a un máximo de 12 bins.
    numero_bins = min(12, max(1, len(precios)))

    fig_precio = px.histogram(
        df_filtrado,
        x="Precio_VTA_MM",
        nbins=numero_bins,
        title="Distribución del precio de venta",
        labels={
            "Precio_VTA_MM": "Precio de venta (millones de pesos)",
            "count": "Cantidad de inmuebles"
        }
    )

    fig_precio.update_layout(
        bargap=0.05,
        yaxis_title="Cantidad de inmuebles",
        xaxis_title="Precio de venta (MM)"
    )

    st.plotly_chart(
        fig_precio,
        use_container_width=True
    )

else:

    st.warning(
        "No existen valores de precio disponibles para mostrar el histograma."
    )


# ============================================================
# GRÁFICO 4
# DISTRIBUCIÓN POR TIPO DE INMUEBLE
# ============================================================

st.subheader("4️⃣ Distribución por Tipo de Inmueble")

datos_tipo = (
    df_filtrado["Tipo_Inmueble"]
    .value_counts()
    .reset_index()
)

datos_tipo.columns = [
    "Tipo_Inmueble",
    "Cantidad"
]

datos_tipo = datos_tipo.sort_values(
    "Cantidad",
    ascending=True
)

fig_tipo = px.bar(
    datos_tipo,
    x="Cantidad",
    y="Tipo_Inmueble",
    orientation="h",
    text="Cantidad",
    title="Cantidad de inmuebles por tipo",
    labels={
        "Cantidad": "Número de inmuebles",
        "Tipo_Inmueble": "Tipo de inmueble"
    }
)

fig_tipo.update_traces(
    textposition="outside"
)

fig_tipo.update_layout(
    height=max(450, len(datos_tipo) * 30),
    showlegend=False,
    margin=dict(l=20, r=50, t=60, b=20)
)

st.plotly_chart(
    fig_tipo,
    use_container_width=True
)


# ============================================================
# GRÁFICO 5
# DISTRIBUCIÓN POR ESTADO DEL INMUEBLE
# ============================================================

st.subheader("5️⃣ Distribución por Estado del Inmueble")

datos_estado = (
    df_filtrado["Estado_Inmueble"]
    .value_counts()
    .reset_index()
)

datos_estado.columns = [
    "Estado_Inmueble",
    "Cantidad"
]

datos_estado = datos_estado.sort_values(
    "Cantidad",
    ascending=True
)

fig_estado = px.bar(
    datos_estado,
    x="Cantidad",
    y="Estado_Inmueble",
    orientation="h",
    text="Cantidad",
    title="Cantidad de inmuebles según estado",
    labels={
        "Cantidad": "Número de inmuebles",
        "Estado_Inmueble": "Estado del inmueble"
    }
)

fig_estado.update_traces(
    textposition="outside"
)

fig_estado.update_layout(
    height=max(400, len(datos_estado) * 35),
    showlegend=False,
    margin=dict(l=20, r=50, t=60, b=20)
)

st.plotly_chart(
    fig_estado,
    use_container_width=True
)


# ============================================================
# TABLA DE DATOS
# ============================================================

with st.expander("📋 Ver datos filtrados"):

    st.dataframe(
        df_filtrado,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PIE DE PÁGINA
# ============================================================

st.divider()

st.caption(
    "Dashboard estadístico — Inmuebles CISA | "
    "Desarrollado con Python, Streamlit y Plotly Express"
)