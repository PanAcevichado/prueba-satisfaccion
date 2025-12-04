import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Dashboard de Satisfacción", layout="wide")

st.title("📊 Análisis de Satisfacción-UNALM 2024-2(Carga tu archivo)")
st.markdown("---")

# --- 2. DICCIONARIO DE VARIABLES ---
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

# --- 3. BARRA LATERAL (SIDEBAR) PARA CARGAR ARCHIVO ---
st.sidebar.header("1. Carga de Datos")
st.sidebar.markdown("Sube tu archivo CSV o Excel aquí:")

# Este es el componente mágico: File Uploader
archivo_cargado = st.sidebar.file_uploader("Arrastra tu archivo aquí", type=["csv", "xlsx"])

# --- 4. LÓGICA DE CARGA ---
if archivo_cargado is not None:
    # Determinar si es CSV o Excel y leerlo
    try:
        if archivo_cargado.name.endswith('.csv'):
            # Intentamos leer CSV (probamos dos codificaciones comunes)
            try:
                df = pd.read_csv(archivo_cargado)
            except UnicodeDecodeError:
                archivo_cargado.seek(0) # Reiniciar el puntero del archivo
                df = pd.read_csv(archivo_cargado, encoding='latin-1')
        else:
            # Si es Excel
            df = pd.read_excel(archivo_cargado)
            
        st.sidebar.success("¡Archivo cargado correctamente!")
        
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        st.stop()

    # --- 5. VERIFICACIÓN DE COLUMNAS ---
    # Revisamos si las columnas V1, V2 existen
    cols_presentes = [col for col in diccionario_preguntas.keys() if col in df.columns]
    
    if len(cols_presentes) == 0:
        st.error("⚠️ El archivo cargado no parece tener las columnas correctas (V1, V2, etc.).")
        st.write("Columnas encontradas:", df.columns.tolist())
        st.stop()

    # --- 6. VISUALIZACIÓN DEL DASHBOARD ---
    
    st.sidebar.header("2. Filtros de Visualización")
    opcion = st.sidebar.radio("Elige una vista:", ["Ranking General", "Detalle por Pregunta"])

    if opcion == "Ranking General":
        st.subheader("🏆 Ranking de Satisfacción Promedio")
        
        # Calcular promedios solo de las columnas válidas
        promedios = df[cols_presentes].mean().sort_values().reset_index()
        promedios.columns = ['Variable', 'Puntaje']
        promedios['Pregunta'] = promedios['Variable'].map(diccionario_preguntas)
        
        # Gráfico de barras
        fig = px.bar(promedios, x='Puntaje', y='Pregunta', orientation='h',
                     text_auto='.2f', color='Puntaje',
                     color_continuous_scale=['#FF4B4B', '#FFD700', '#2ECC71'], # Rojo, Amarillo, Verde
                     range_x=[1, 5])
        
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        # KPIs rápidos
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Encuestados", len(df))
        col2.metric("Promedio Global", f"{df[cols_presentes].mean().mean():.2f}")
        col3.metric("Peor aspecto", promedios.iloc[0]['Pregunta'])

    elif opcion == "Detalle por Pregunta":
        st.subheader("🔍 Análisis Detallado")
        
        nombres_disponibles = [diccionario_preguntas[c] for c in cols_presentes]
        seleccion_nombre = st.selectbox("Selecciona la variable:", nombres_disponibles)
        
        # Obtener código (V1, V2...) inverso
        codigo_sel = [k for k, v in diccionario_preguntas.items() if v == seleccion_nombre][0]
        
        # Gráfico
        conteos = df[codigo_sel].value_counts().sort_index().reset_index()
        conteos.columns = ['Puntaje', 'Votos']
        
        col_g, col_d = st.columns([2, 1])
        
        with col_g:
            fig_pie = px.pie(conteos, values='Votos', names='Puntaje', 
                             title=f"Distribución: {seleccion_nombre}",
                             hole=0.4) # Gráfico de dona
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_d:
            st.info(f"**Media:** {df[codigo_sel].mean():.2f}")
            st.warning(f"**Desv. Estándar:** {df[codigo_sel].std():.2f}")
            st.dataframe(conteos, hide_index=True)

    # Mostrar datos crudos al final
    with st.expander("Ver tabla de datos completa"):
        st.dataframe(df)

else:
    # --- MENSAJE DE BIENVENIDA (CUANDO NO HAY ARCHIVO) ---
    st.info("👈 Por favor, utiliza el menú de la izquierda para subir tu archivo CSV o Excel.")
    st.markdown("""
    **Requisitos del archivo:**
    * Debe contener columnas nombradas como **V1, V2, ... V17**.
    * Los valores deben ser números del 1 al 5.
    """)
    
    # Imagen de ejemplo (opcional, para decorar)
    # st.image("https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", width=200)

