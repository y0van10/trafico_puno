import streamlit as st
import requests
import os
import pandas as pd
import pydeck as pdk
import json
from datetime import datetime

# Configuración de página con estética premium
st.set_page_config(
    page_title="PunoTraffic AI — Simulador MLOps Didáctico",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para UI/UX de alta calidad
st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }
    .stApp {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
    }
    /* Estilo de Tarjetas Modernas */
    .metric-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.7);
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    /* Insignias de Nivel de Tráfico */
    .traffic-badge {
        padding: 8px 16px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-block;
        margin-top: 8px;
        text-align: center;
    }
    .badge-green {
        background-color: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
    }
    .badge-orange {
        background-color: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
    }
    .badge-red {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
    }
    /* Banner de Estado */
    .status-banner {
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .status-active {
        background-color: #ecfdf5;
        color: #065f46;
        border: 1px solid #a7f3d0;
    }
    .status-simulated {
        background-color: #fffbeb;
        color: #92400e;
        border: 1px solid #fde68a;
    }
    /* Títulos e Iconografía */
    .gradient-text {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# Coordenadas geográficas reales y metadatos de las zonas en Puno
ZONES_DATA = {
    'Centro': {
        "lat": -15.840222,
        "lon": -70.027806,
        "desc": "Plaza de Armas y Jr. Lima. Zona comercial e histórica. Vías angostas con alta presencia de peatones y vehículos oficiales."
    },
    'Bellavista': {
        "lat": -15.834028,
        "lon": -70.030556,
        "desc": "Barrio comercial y residencial (cerca al mercado Bellavista). Calles con flujo dinámico de colectivos y mototaxis."
    },
    'Salcedo': {
        "lat": -15.861500,
        "lon": -70.003500,
        "desc": "Zona sur de expansión urbana. Concentra colegios, institutos y el Hospital Regional. Picos en horas de entrada y salida."
    },
    'Huaje': {
        "lat": -15.820500,
        "lon": -70.019500,
        "desc": "Acceso norte de la ciudad (Vía a Juliaca). Alta circulación de transporte interprovincial, camiones pesados y colectivos."
    },
    'Terminal': {
        "lat": -15.844500,
        "lon": -70.016000,
        "desc": "Terminal Terrestre y alrededores. Punto de llegada de buses nacionales e interprovinciales. Alta densidad de taxis y colectivos."
    }
}

# Climas y días útiles para traducción
DAYS_SPANISH = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Configuración de API
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

# Función de simulación en caso de que el backend FastAPI esté desconectado (Resiliencia Didáctica)
def run_simulated_prediction(zone, hour, day_of_week, weather):
    # Nivel base por zona
    base = {
        'Centro': 45.0,
        'Terminal': 50.0,
        'Bellavista': 30.0,
        'Salcedo': 20.0,
        'Huaje': 15.0
    }.get(zone, 25.0)
    
    # Factor de Hora (Picos en 7-9 AM, 12-2 PM y 6-8 PM)
    if 7 <= hour <= 9:
        hour_factor = 2.2
    elif 12 <= hour <= 14:
        hour_factor = 1.8
    elif 18 <= hour <= 20:
        hour_factor = 2.1
    elif 0 <= hour <= 5:
        hour_factor = 0.25
    else:
        hour_factor = 1.1
        
    # Factor de Clima
    weather_factor = {
        'Soleado': 0.85,
        'Nublado': 1.05,
        'Lluvioso': 1.45,
        'Nevada': 1.75
    }.get(weather, 1.0)
    
    # Factor de Día de la semana (Lunes de inicio, Viernes y Sábados más congestionados en Puno)
    day_factor = 1.25 if day_of_week in [0, 4, 5] else 0.9
    
    # Cálculo final con ruido simulado
    result = base * hour_factor * weather_factor * day_factor
    return float(max(5.0, min(99.0, round(result, 2))))

# Función para consultar el Backend
def get_prediction(zone, hour, day_of_week, weather):
    try:
        payload = {
            "hour": hour,
            "day_of_week": day_of_week,
            "weather": weather,
            "zone": zone
        }
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=2.0)
        if response.status_code == 200:
            return response.json()["predicted_traffic_level"], "Producción (FastAPI/XGBoost)"
    except Exception:
        pass
    # Fallback si falla la conexión
    return run_simulated_prediction(zone, hour, day_of_week, weather), "Simulador Didáctico (Reglas Locales)"

# --- CABECERA PRINCIPAL ---
st.markdown("""
<div style='text-align: center; margin-bottom: 25px;'>
    <h1 style='margin-bottom: 0px;'><span class='gradient-text'>🚦 PunoTraffic AI</span></h1>
    <p style='color: #64748b; font-size: 1.2rem; font-weight: 500; margin-top: 5px;'>
        Simulador Inteligente y Didáctico de Congestión Vehicular - Puno, Perú
    </p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR DE CONTROL ---
st.sidebar.markdown("""
<div style='text-align: center; margin-bottom: 15px;'>
    <h3 style='margin:0;'>🎮 Panel de Simulación</h3>
    <small style='color: #64748b;'>Ajusta las variables físicas del entorno</small>
</div>
""", unsafe_allow_html=True)

selected_zone = st.sidebar.selectbox(
    "📍 Seleccionar Zona Principal",
    options=list(ZONES_DATA.keys()),
    index=0,
    help="Zona central sobre la que se desplegará el análisis didáctico detallado."
)

hour = st.sidebar.slider(
    "⏰ Hora del Día",
    min_value=0,
    max_value=23,
    value=datetime.now().hour,
    format="%d:00 hrs",
    help="Desplaza el control para simular la variación del tráfico hora por hora."
)

day_name = st.sidebar.selectbox(
    "📅 Día de la Semana",
    options=DAYS_SPANISH,
    index=datetime.today().weekday(),
    help="El flujo vial en Puno cambia drásticamente en días laborables vs fines de semana."
)
day_of_week = DAYS_SPANISH.index(day_name)

weather = st.sidebar.select_slider(
    "🌧️ Condición Climática",
    options=["Soleado", "Nublado", "Lluvioso", "Nevada"],
    value="Soleado",
    help="El clima altera directamente las velocidades del tránsito en la altura puneña."
)

st.sidebar.markdown("---")

# Verificar el estado de conexión del backend en segundo plano
backend_active = False
try:
    health_resp = requests.get(f"{API_URL}/health", timeout=1.0)
    if health_resp.status_code == 200:
        backend_active = True
except Exception:
    pass

if backend_active:
    st.sidebar.markdown("""
    <div class='status-banner status-active'>
        🟢 <b>CONECTADO</b><br>API de Producción XGBoost Activa
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div class='status-banner status-simulated'>
        ⚠️ <b>MODO DE SIMULACIÓN</b><br>API desconectada. Ejecutando reglas didácticas locales.
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("""
<div style='font-size: 0.8rem; color: #64748b; text-align: center; margin-top: 20px;'>
    Desarrollado para el curso de <b>Aprendizaje de Máquina</b><br>Universidad Nacional del Altiplano - Puno
</div>
""", unsafe_allow_html=True)

# --- OBTENER PREDICCIONES PARA TODAS LAS ZONAS ---
predictions = {}
source_engine = "Simulador"
for zone_name in ZONES_DATA.keys():
    pred_val, engine = get_prediction(zone_name, hour, day_of_week, weather)
    predictions[zone_name] = pred_val
    source_engine = engine

# --- DISEÑO DE PESTAÑAS (INCLUYENDO LA DE DEVOPS/MLOPS) ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Mapa e Interacción en Tiempo Real", 
    "🧠 Aula Interactiva (¿Cómo piensa la IA?)", 
    "📊 Telemetría y Análisis de Datos",
    "⚙️ MLOps & Pipeline CI/CD"
])

with tab1:
    col_left, col_right = st.columns([1.1, 0.9])
    
    with col_left:
        st.markdown("### 🗺️ Mapa de Congestión en OpenStreetMap (Puno)")
        st.markdown(
            "Visualiza el nivel de congestión vehicular simulado para todas las zonas de Puno simultáneamente. "
            "El tamaño y color de los círculos cambian dinámicamente según el tráfico."
        )
        
        # Preparación de datos para PyDeck
        map_data = []
        for name, coord in ZONES_DATA.items():
            traffic = predictions[name]
            
            # Color basado en el nivel de tráfico (Verde -> Amarillo/Naranja -> Rojo)
            if traffic < 30:
                color = [34, 197, 94, 180]  # Verde
            elif traffic < 70:
                color = [245, 158, 11, 200]  # Naranja
            else:
                color = [239, 68, 68, 220]   # Rojo
                
            is_selected = name == selected_zone
            map_data.append({
                "name": name,
                "lat": coord["lat"],
                "lon": coord["lon"],
                "traffic": traffic,
                "color": color,
                # El círculo de la zona seleccionada es más grande y brillante
                "radius": (250 + (traffic * 4)) if not is_selected else (400 + (traffic * 5)),
                "line_color": [30, 58, 138, 255] if is_selected else [255, 255, 255, 180],
                "line_width": 4 if is_selected else 1.5
            })
            
        df_map = pd.DataFrame(map_data)
        
        # Configurar la capa de Pydeck en OpenStreetMap
        layer = pdk.Layer(
            "ScatterplotLayer",
            df_map,
            get_position="[lon, lat]",
            get_color="color",
            get_radius="radius",
            get_line_color="line_color",
            get_line_width="line_width",
            pickable=True,
            opacity=0.85,
            stroked=True,
            filled=True,
        )
        
        # Centrar el mapa en la zona seleccionada
        sel_coord = ZONES_DATA[selected_zone]
        view_state = pdk.ViewState(
            latitude=sel_coord["lat"] - 0.003, # offset para encuadre
            longitude=sel_coord["lon"],
            zoom=13.6,
            pitch=35
        )
        
        # Renderizado del mapa interactivo
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9" if os.getenv("MAPBOX_API_KEY") else "road",
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"html": "<b>Zona:</b> {name}<br><b>Congestión:</b> {traffic}%", "style": {"color": "white", "backgroundColor": "#1e293b", "borderRadius": "8px"}}
        ))
        
        st.caption("ℹ️ Puedes mantener presionado el botón derecho del mouse para rotar el mapa en 3D.")
        
    with col_right:
        # Ficha didáctica de la zona seleccionada
        sel_traffic = predictions[selected_zone]
        
        if sel_traffic < 30:
            badge_class = "badge-green"
            status_text = "Tráfico Fluido (Baja Congestión)"
            desc_alert = "🚗 La circulación es óptima. Excelente momento para desplazarse por esta zona sin demoras."
        elif sel_traffic < 70:
            badge_class = "badge-orange"
            status_text = "Tráfico Moderado (Concurrencia)"
            desc_alert = "🟡 Flujo regular con pequeñas retenciones en semáforos. Desplazamientos normales con precaución."
        else:
            badge_class = "badge-red"
            status_text = "Tráfico Pesado (Embotellamiento)"
            desc_alert = "🚨 Alta densidad vehicular. Retrasos significativos asegurados. Se sugiere tomar vías alternas."

        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='margin: 0;'>📍 Análisis Detallado: Zona {selected_zone}</h3>
            <p style='color: #64748b; font-size: 0.9rem; margin-top: 5px;'>{ZONES_DATA[selected_zone]['desc']}</p>
            <hr style='margin: 15px 0;'>
            <div style='display: flex; align-items: baseline; gap: 10px;'>
                <span style='font-size: 3rem; font-weight: 800; color: #1e3a8a;'>{sel_traffic}%</span>
                <span style='color: #64748b; font-weight: 600;'>de congestión estimada</span>
            </div>
            <div class='traffic-badge {badge_class}'>
                {status_text}
            </div>
            <div style='margin-top: 15px; font-size: 0.95rem; color: #334155; line-height: 1.5;'>
                {desc_alert}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Explicador Didáctico de Factores Activos
        st.markdown("### 🧩 Factores que influyen en esta predicción:")
        
        # Lógica didáctica para explicar qué causó la predicción
        explanations = []
        
        # 1. Hora
        if 7 <= hour <= 9:
            explanations.append("⏰ **Hora Pico Escolar/Laboral (+30%):** Es el momento de ingreso a colegios y oficinas en Puno. Gran masa de autos particulares y colectivos en ruta.")
        elif 12 <= hour <= 14:
            explanations.append("⏰ **Hora Pico del Almuerzo (+15%):** Desplazamiento comercial masivo y retorno de escolares a sus hogares.")
        elif 18 <= hour <= 20:
            explanations.append("⏰ **Hora Pico de Retorno (+25%):** Salida del trabajo e institutos. Gran concentración vial en las vías conectoras.")
        else:
            explanations.append("⏰ **Hora Valle (-20%):** Flujo regular de vehículos sin picos de demanda masiva.")
            
        # 2. Clima
        if weather == "Lluvioso":
            explanations.append("🌧️ **Clima Lluvioso (+20%):** El asfalto mojado y la visibilidad reducida obligan a bajar las velocidades en Puno, incrementando las colas vehiculares.")
        elif weather == "Nevada":
            explanations.append("❄️ **Clima de Nevada (+35%):** El granizo/nieve en las partes altas (ej. Huaje o accesos) congela la calzada, provocando congestión severa por seguridad vial.")
        else:
            explanations.append("☀️ **Clima Favorable (-10%):** Visibilidad normal y asfalto seco permiten un tránsito a velocidades de diseño normales.")
            
        # 3. Día
        if day_of_week in [0, 4, 5]:
            explanations.append("📅 **Día de Alta Concurrencia (+10%):** Inicio de semana (lunes) o víspera/fin de semana (viernes/sábado) donde se incrementan los viajes comerciales y sociales en Puno.")
        else:
            explanations.append("📅 **Día Inmediato (Tránsito Regular):** Flujo estándar de media semana.")

        for exp in explanations:
            st.markdown(f"- {exp}")
            
        st.info(f"💡 **Motor de Cálculo:** Predicción generada usando el modelo **{source_engine}**.")

with tab2:
    st.markdown("## 🧠 Aula Interactiva de Inteligencia Artificial")
    st.markdown(
        "¡Bienvenido al rincón académico! Aquí aprenderás cómo el algoritmo de Machine Learning "
        "toma las variables físicas de Puno y las convierte en una predicción precisa."
    )
    
    col_edu1, col_edu2 = st.columns(2)
    
    with col_edu1:
        st.markdown("### 🌲 ¿Cómo funciona el Algoritmo XGBoost?")
        st.markdown("""
        **XGBoost** (eXtreme Gradient Boosting) es una técnica basada en **Árboles de Decisión**. 
        En lugar de usar un solo árbol gigante, XGBoost crea **cientos de árboles pequeños y sencillos**, 
        donde cada árbol nuevo aprende y corrige los errores del árbol anterior de forma secuencial.
        
        Para entenderlo de forma didáctica, imagina que el algoritmo funciona como un comité de expertos 
        viales puneños que van afinando su respuesta uno tras otro hasta dar el diagnóstico final.
        """)
        
        st.markdown("#### 📉 El Árbol de Decisión Didáctico")
        st.markdown(
            "A continuación puedes ver un ejemplo simplificado de cómo un solo árbol del modelo "
            "toma decisiones lógicas en cascada:"
        )
        
        # Representación gráfica limpia del árbol de decisiones
        st.code("""
                   [¿Es Hora Pico (7-9 AM, 12-2 PM, 6-8 PM)?]
                            /                     \\
                          SÍ                       NO
                         /                           \\
       [¿El Clima es Lluvioso/Nevada?]       [¿La Zona es Centro/Terminal?]
                 /          \\                         /          \\
               SÍ            NO                     SÍ            NO
              /                \\                   /                \\
       [Tráfico: 85%]     [Tráfico: 55%]     [Tráfico: 45%]     [Tráfico: 15%]
        """, language="text")
        
    with col_edu2:
        st.markdown("### 🎮 Simulador Manual del Árbol de Decisión")
        st.markdown(
            "Juega a ser el algoritmo. Sigue el flujo del árbol de decisión interactivo "
            "respondiendo las siguientes preguntas lógicas sobre tu simulación actual:"
        )
        
        # Simulador del juego interactivo
        is_rush_hour = (7 <= hour <= 9) or (12 <= hour <= 14) or (18 <= hour <= 20)
        is_bad_weather = weather in ["Lluvioso", "Nevada"]
        is_dense_zone = selected_zone in ["Centro", "Terminal"]
        
        st.markdown(f"**Paso 1:** ¿Es hora pico en tu simulación actual? (Hora actual: {hour}:00) ")
        st.markdown(f"👉 Respuesta lógica: **{'SÍ' if is_rush_hour else 'NO'}**")
        
        if is_rush_hour:
            st.markdown(f"**Paso 2 (Rama Izquierda):** ¿El clima es adverso? (Clima actual: {weather})")
            st.markdown(f"👉 Respuesta lógica: **{'SÍ' if is_bad_weather else 'NO'}**")
            
            if is_bad_weather:
                final_node = "🔴 **[Nodo Terminal: Tráfico Pesado (85%)]**"
                explanation_node = "Al coincidir una hora de alta demanda escolar/laboral con una pista húmeda/congelada, la velocidad urbana en Puno cae al mínimo."
            else:
                final_node = "🟡 **[Nodo Terminal: Tráfico Moderado (55%)]**"
                explanation_node = "A pesar de la alta demanda escolar/laboral, el clima soleado/despejado permite un flujo vehicular regular."
        else:
            st.markdown(f"**Paso 2 (Rama Derecha):** ¿La zona seleccionada es de alta densidad? (Zona seleccionada: {selected_zone})")
            st.markdown(f"👉 Respuesta lógica: **{'SÍ' if is_dense_zone else 'NO'}**")
            
            if is_dense_zone:
                final_node = "🟡 **[Nodo Terminal: Tráfico Moderado (45%)]**"
                explanation_node = "Fuera de hora pico, zonas críticas como el Centro y el Terminal Terrestre mantienen un tráfico constante debido a la actividad comercial de Puno."
            else:
                final_node = "🟢 **[Nodo Terminal: Tráfico Bajo/Fluido (15%)]**"
                explanation_node = "En horas tranquilas y en zonas residenciales/periféricas (como Salcedo o Huaje), el flujo vehicular puneño es totalmente libre."
                
        st.markdown("---")
        st.markdown(f"#### 🏆 Predicción del Árbol Manual:")
        st.markdown(final_node)
        st.markdown(explanation_node)

with tab3:
    st.markdown("## 📊 Telemetría y Análisis de Datos Históricos (Puno)")
    st.markdown(
        "En esta pestaña puedes analizar el comportamiento global de las variables del simulador "
        "y cómo impactan en la congestión de Puno a nivel estadístico."
    )
    
    col_graph1, col_graph2 = st.columns(2)
    
    with col_graph1:
        st.markdown("### 📈 Perfil de Congestión a lo Largo del Día")
        st.markdown(
            "Este gráfico muestra la evolución típica del tráfico durante las 24 horas del día. "
            "Observa las tres crestas pronunciadas (picos) comunes de la ciudad."
        )
        
        # Generar datos simulados de 24 horas para la zona actual
        profile_data = []
        for h in range(24):
            val, _ = get_prediction(selected_zone, h, day_of_week, weather)
            profile_data.append({"Hora": f"{h:02d}:00", "Congestión %": val})
        df_profile = pd.DataFrame(profile_data)
        
        st.line_chart(df_profile.set_index("Hora"))
        
    with col_graph2:
        st.markdown("### 📊 Comparativa de Congestión por Clima y Zona")
        st.markdown(
            "Compara cómo afectaría cada una de las condiciones climáticas a la zona "
            "seleccionada en la hora simulada actual."
        )
        
        weather_compare = []
        for w in ["Soleado", "Nublado", "Lluvioso", "Nevada"]:
            val, _ = get_prediction(selected_zone, hour, day_of_week, w)
            weather_compare.append({"Clima": w, "Congestión %": val})
        df_weather = pd.DataFrame(weather_compare)
        
        st.bar_chart(df_weather.set_index("Clima"))
        
    st.markdown("---")
    st.markdown("### 🥇 Ranking de Congestión de Zonas en Puno")
    st.markdown(
        "A continuación se presenta un ranking en tiempo real de todas las zonas de la ciudad para las condiciones actuales de simulación:"
    )
    
    # Crear tabla de clasificación
    ranking_data = []
    for name in ZONES_DATA.keys():
        ranking_data.append({
            "Zona de Puno": name,
            "Congestión Vehicular": f"{predictions[name]}%",
            "Clasificación": "🔴 Pesado" if predictions[name] >= 70 else ("🟡 Moderado" if predictions[name] >= 30 else "🟢 Fluido")
        })
    df_ranking = pd.DataFrame(ranking_data).sort_values(by="Congestión Vehicular", ascending=False)
    st.dataframe(df_ranking, use_container_width=True)

with tab4:
    st.markdown("## ⚙️ Arquitectura MLOps y Pipelines Automatizados (CI/CD)")
    st.markdown(
        "Esta sección expone los flujos de integración continua, pruebas de regresión y el "
        "pipeline de mantenimiento inteligente que da soporte a esta aplicación inteligente durante su ciclo de vida."
    )
    
    col_dev1, col_dev2 = st.columns(2)
    
    with col_dev1:
        st.markdown("""
        ### 🔄 1. Integración y Despliegue Continuo (CI/CD)
        Cada cambio de código o actualización del modelo de datos activa un flujo automatizado de integración en la nube a través de **GitHub Actions** (`ci_cd.yml`):
        
        *   **Linting de Código:** Validación PEP 8 estricta con `flake8` en `/backend` y `/ml_pipeline` para garantizar código limpio y profesional.
        *   **Pruebas de Inferencia:** Ejecución de entrenamiento del pipeline de ML autónomo para garantizar consistencia lógica antes de pruebas.
        *   **Pruebas Unitarias y de Integración:** Ejecución de **20 pruebas de integridad** con `pytest` en backend, validando la inmunidad del servidor ante entradas inválidas o desbordamientos.
        *   **Compilación e Inyección Segura:** Generación de contenedores productivos Docker a través de *Multi-Stage builds* asegurando que corran con un usuario no root (`appuser`) para una seguridad robusta.
        """)
        
        st.code("""
 PUSH/PR ──> [Calidad: flake8] ──> [ML: train.py] ──> [Tests: 20 Pytests] ──> [Docker Build & Deploy]
        """, language="text")
        
    with col_dev2:
        st.markdown("""
        ### 🔄 2. Mantenimiento y Retraining Automatizado
        Para evitar la degradación del modelo (**Model Drift**) a medida que cambian los comportamientos viales puneños, el pipeline cuenta con un flujo de mantenimiento continuo inteligente en `retrain.py`:
        
        *   **Ingesta y Optimización:** El reentrenamiento ingiere nuevos datos viales de Puno y ejecuta una optimización masiva de hiperparámetros ganadores (`GridSearchCV` evaluando **108 combinaciones** en paralelo).
        *   **Promoción Segura:** Compara el nuevo coeficiente de determinación $R^2$ candidato contra el del modelo productivo activo.
        *   **Filtro Inteligente:** Si el nuevo modelo degrada su precisión en más del 5% (indicio de datos ruidosos o sesgados), **el pipeline cancela la actualización de forma automática** y lanza una alerta técnica preventiva al equipo de TI, impidiendo corromper la API activa.
        """)
        
    st.markdown("---")
    st.markdown("### 📊 Historial y Trazabilidad de Modelos en Producción (MLOps Telemetry)")
    st.markdown(
        "A continuación se extrae la información en tiempo real del archivo persistente `metrics_history.json`. "
        "Este registro almacena las métricas de rendimiento y los hiperparámetros optimizados de cada versión del cerebro inteligente del sistema:"
    )
    
    # Intentar leer metrics_history.json de forma robusta
    metrics_path = ""
    paths_to_try = [
        "../ml_pipeline/models/metrics_history.json",
        "ml_pipeline/models/metrics_history.json",
        "./ml_pipeline/models/metrics_history.json",
        "../../ml_pipeline/models/metrics_history.json"
    ]
    for p in paths_to_try:
        if os.path.exists(p):
            metrics_path = p
            break
            
    if metrics_path:
        try:
            with open(metrics_path, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            # Convertir a DataFrame legible
            history_rows = []
            for entry in sorted(history_data, key=lambda x: x.get('trained_at', ''), reverse=True):
                history_rows.append({
                    "Versión": entry.get("version"),
                    "R² (Precisión de Predicción)": f"{entry.get('r2') * 100:.2f}%" if entry.get('r2') is not None else "N/A",
                    "Error Absoluto Medio (MAE)": entry.get("mae"),
                    "Error Cuadrático Medio (MSE)": entry.get("mse"),
                    "Registros Entrenados": entry.get("data_records"),
                    "Hiperparámetros Optimizados (Ganadores)": str(entry.get("best_params")),
                    "Fecha de Entrenamiento (UTC)": entry.get("trained_at", "")[:19].replace("T", " ")
                })
            
            df_history = pd.DataFrame(history_rows)
            st.dataframe(df_history, use_container_width=True)
            
        except Exception as e:
            st.error(f"No se pudo cargar la telemetría histórica: {e}")
    else:
        st.warning("⚠️ Archivo de historial de telemetría `metrics_history.json` no encontrado en el servidor.")