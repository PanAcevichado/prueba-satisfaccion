import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Dashboard de Satisfacción", layout="wide")
st.title("📊 Análisis de Satisfacción - UNALM 2024-2")

# --- 2. DICCIONARIO DE PREGUNTAS (V1 a V17) ---
# Esto sirve para que los gráficos muestren el texto y no solo "V1"
diccionario_preguntas = {
    "V1": "Apertura de aulas a tiempo",
    "V2": "Aire acondicionado",
    "V3": "Arreglo de cortinas",
    "V4": "Calefacción",
    "V5": "Equipos",
    "V6": "Horario servicios higiénicos",
    "V7": "Limpieza de ambiente",
    "V8": "Ambiente",
    "V9": "Iluminación",
    "V10": "Trato personal",
    "V11": "Mobiliario",
    "V12": "Ruido",
    "V13": "Ventilación",
    "V14": "Ambientes Modernos",
    "V15": "Dictado de clases",
    "V16": "Internet",
    "V17": "Sistema eléctrico"
}

# --- 3. CARGA DE DATOS ---
@st.cache_data
def cargar_datos():
    archivo = "datos-satisfaccion.xlsx"
    try:
        # Intentamos leer con codificación estándar
        df = pd.read_excel(archivo)
    except UnicodeDecodeError:
        # Si falla por tildes, probamos con latin-1 (común en Excel en español)
        df = pd.read_excel(archivo, encoding='latin-1')
    
    return df

try:
    df = cargar_datos()
    
    # --- VERIFICACIÓN DE COLUMNAS (DEBUG) ---
    # Esto es vital: Si tus columnas en el Excel no se llaman "V1", "V2"...
    # el dashboard fallará. Aquí revisamos si existen.
    cols_presentes = [col for col in diccionario_preguntas.keys() if col in df.columns]
    
    if len(cols_presentes) < 5:
        st.error("⚠️ Alerta: No encuentro las columnas V1, V2, etc. en tu archivo.")
        st.write("Las columnas detectadas son:", df.columns.tolist())
        st.stop()
        
except FileNotFoundError:
    st.error(f"⚠️ No encuentro el archivo. Asegúrate de que 'datos-satisfaccion.xlsx' esté en la misma carpeta que este script.")
    st.stop()

# --- 4. PANEL DE CONTROL (SIDEBAR) ---
st.sidebar.header("Filtros")
opcion = st.sidebar.radio("Vista:", ["Ranking General", "Detalle por Pregunta"])

# --- 5. VISUALIZACIÓN ---

if opcion == "Ranking General":
    st.subheader("Ranking: ¿Qué es lo mejor y peor evaluado?")
    
    # Calculamos el promedio solo de las columnas V1-V17 que existan en el archivo
    columnas_analisis = [c for c in diccionario_preguntas.keys() if c in df.columns]
    promedios = df[columnas_analisis].mean().sort_values().reset_index()
    promedios.columns = ['Variable', 'Puntaje']
    
    # Ponemos los nombres bonitos
    promedios['Pregunta'] = promedios['Variable'].map(diccionario_preguntas)
    
    # Gráfico de barras
    fig = px.bar(promedios, x='Puntaje', y='Pregunta', orientation='h',
                 text_auto='.2f', color='Puntaje',
                 color_continuous_scale=['red', 'yellow', 'green'], range_x=[1, 5])
    
    st.plotly_chart(fig, use_container_width=True)

elif opcion == "Detalle por Pregunta":
    st.subheader("Análisis detallado")
    
    # Seleccionar pregunta por nombre real
    nombres_preguntas = list(diccionario_preguntas.values())
    seleccion = st.selectbox("Elige un aspecto a analizar:", nombres_preguntas)
    
    # Buscar el código (ej. "V1") a partir del nombre
    codigo = [k for k, v in diccionario_preguntas.items() if v == seleccion][0]
    
    if codigo in df.columns:
        # Gráfico de pastel de distribución
        datos_conteo = df[codigo].value_counts().reset_index()
        datos_conteo.columns = ['Calificación', 'Cantidad']
        
        col1, col2 = st.columns([2, 1])
        with col1:
            fig_pie = px.pie(datos_conteo, values='Cantidad', names='Calificación', 
                             title=f"Distribución de votos: {seleccion}")
            st.plotly_chart(fig_pie)
        with col2:
            st.metric("Promedio", f"{df[codigo].mean():.2f} / 5")
            st.metric("Desviación", f"{df[codigo].std():.2f}")
            st.write(f"Total respuestas: {df[codigo].count()}")

# --- 6. MOSTRAR DATOS (Al final) ---
with st.expander("Ver base de datos cargada"):
    st.dataframe(df)



