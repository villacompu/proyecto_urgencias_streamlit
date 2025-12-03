import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import pickle
import numpy as np
import time

# -----------------------------------------------------
# MAPEOS (Variables del entrenamiento)
# -----------------------------------------------------
map_sexo = {"M": 1, "F": 0}

map_regimen = {
    "Subsidiado": 1,
    "Contributivo": 2,
    "Especial": 3,
    "Particular": 4,
    "Otro": 5
}

map_triaje = {"I": 0, "II": 1, "III": 2, "IV": 3, "V": 4}

map_urgencia_xpress = {"Sí": 1, "No": 0}

map_servicio_habilitado = {
    "URGENCIAS ADULTO": 0,
    "URGENCIAS PEDIATRICAS": 1
}

map_entidad_responsable = {
    "NUEVA EPS S.A.": 0,
    "COOSALUD EPS": 1,
    "ALIANZA MEDELLIN ANTIOQUIA EPS S.A.S": 2,
    "EPS SURAMERICANA S.A": 3
}

map_servicio_ingreso = {
    "URGENCIAS GENERALES SÓTANO": 0,
    "URGENCIAS PEDIÁTRICAS": 1
}

map_ubicacion_triaje = {
    "CONSULTORIO 1": 0,
    "CONSULTORIO 2": 1,
    "CONSULTORIO 3": 2,
    "CONSULTORIO 4": 3,
    "CONSULTORIO ONCOLOGIA": 4,
    "CONSULTORIO PEDIATRIA": 5,
    "URGENCIAS PEDIÁTRICAS": 6,
    "XPRESS": 7
}

dx_principal_capitulo_map = {
    "CAUSAS EXTERNAS DE MORBILIDAD Y DE MORTALIDAD": 0,
    "CIERTAS AFECCIONES ORIGINADAS EN EL PERIODO PERINATAL": 1,
    "CIERTAS ENFERMEDADES INFECCIOSAS Y PARASITARIAS": 2,
    "ENFERMEDADES DEL OIDO Y DE LA APOFISIS MASTOIDES": 3,
    "ENFERMEDADES DEL OJO Y SUS ANEXOS": 4,
    "ENFERMEDADES DEL SISTEMA CIRCULATORIO": 5,
    "ENFERMEDADES DEL SISTEMA DIGESTIVO": 6,
    "ENFERMEDADES DEL SISTEMA GENITOURINARIO": 7,
    "ENFERMEDADES DEL SISTEMA NERVIOSO": 8,
    "ENFERMEDADES DEL SISTEMA OSTEOMUSCULAR Y DEL TEJIDO CONJUNTIVO": 9,
    "ENFERMEDADES DEL SISTEMA RESPIRATORIO": 10
}

dx_principal_tipo_1_map = {  # reingreso
    "NUEVO": 0,
    "REPETIDO": 1
}

dx_principal_tipo_2_map = {  # diagnóstico principal
    "ARTRITIS REUMATOIDE": 0,
    "CANCER": 1,
    "DIABETES": 2,
    "GESTANTES": 3,
    "HEMOFILIA": 4,
    "HEPATITIS C": 5,
    "HIPERTENSION": 6,
    "RENAL": 7,
    "SIN INFORMACIÓN": 8,
    "TUBERCULOSIS": 9,
    "VIH": 10,
    "ZNO ALTO COSTO": 11
}

# -----------------------------------------------------
# CARGAR MODELO
# -----------------------------------------------------
@st.cache_resource
def load_model():
    with open("modelo_urgencias.pkl", "rb") as f:
        return pickle.load(f)

model = load_model()


# -----------------------------------------------------
# DISEÑO
# -----------------------------------------------------
st.set_page_config(page_title="Predicción Urgencias", layout="wide", page_icon="🚑")

st.markdown(
    """
    <style>
        .title {text-align:center; color:#1E88E5; font-size:28px; font-weight:700;}
        .subtitle {text-align:center; color:gray; margin-bottom:18px;}
        .card {
            border-radius:12px;
            padding:16px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            background: linear-gradient(180deg, #ffffff, #f7f9ff);
        }
    </style>
    """,
    unsafe_allow_html=True,
)
st.image("https://almamater.hospital/wp-content/uploads/2023/03/logo-hospital-alma-mater-1.png", width=100,use_container_width=True)

# -----------------------------------------------------
# DISEÑO Y POWER BI EMBED
# -----------------------------------------------------


st.markdown('<div class="title">📈 Indicadores - Power BI integrado</div>', unsafe_allow_html=True)
st.markdown(
    """
    <style>
        .title {text-align:center; color:#1E88E5; font-size:28px; font-weight:700;}
        .subtitle {text-align:center; color:gray; margin-bottom:8px;}
        .card {border-radius:12px; padding:16px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Power BI iframe (incrustado arriba) ----


powerbi_iframe = """
<iframe title="Indicadores fichas de caracterización priorizados" width="100%" height="600"
src="https://app.powerbi.com/view?r=eyJrIjoiMGI5ZTVlNTQtNTczMS00NTg1LWE1OGQtY2ZjMGVlMjZjMDUxIiwidCI6IjQ3MDJjZWJlLWI0ZDgtNGI4Mi04NGVkLTdkMmNjMmU5ZGY1OCJ9"
frameborder="0" allowFullScreen="true"></iframe>
"""


# use components.html to render full-width iframe
components.html(powerbi_iframe, height=600, scrolling=True)

st.markdown('<div class="title">🩺 Predicción de permanencia en Urgencias</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ingresa los datos del paciente (todos los selects mapean a valores numéricos)</div>', unsafe_allow_html=True)


# Imagen decorativa
#st.image("https://almamater.hospital/wp-content/uploads/2023/03/logo-hospital-alma-mater-1.png", width=220)

# -----------------------------------------------------
# FORMULARIO EN 2 COLUMNAS
# -----------------------------------------------------
with st.form("pred_form"):
    col1, col2 = st.columns(2)

    with col1:
        nom_servicio_habilitado = st.selectbox("Servicio habilitado", list(map_servicio_habilitado.keys()))
        edad = st.number_input("Edad", min_value=0, max_value=120, step=1, value=30)
        sexo = st.selectbox("Sexo", list(map_sexo.keys()))
        regimen_afiliacion = st.selectbox("Régimen de afiliación", list(map_regimen.keys()))
        entidad_responsable_pago_validada = st.selectbox("Entidad responsable del pago", list(map_entidad_responsable.keys()))

    with col2:
        clasificacion_1_triaje_enfermeria = st.selectbox("Clasificación 1 triaje (Enfermería)", list(map_triaje.keys()))
        reclasificacion1_triaje_medico = st.selectbox("Reclasificación 1 triaje (Médico)", list(map_triaje.keys()))
        urgencia_xpress_f3 = st.selectbox("Urgencia Xpress F3", list(map_urgencia_xpress.keys()))
        servicio_ingreso = st.selectbox("Servicio ingreso", list(map_servicio_ingreso.keys()))
        ubicacion_triaje = st.selectbox("Ubicación triaje", list(map_ubicacion_triaje.keys()))

    st.markdown("---")
    # Campos que ocupan todo el ancho (debajo de las dos columnas)
    dx_principal_capitulo = st.selectbox("Dx principal capítulo", list(dx_principal_capitulo_map.keys()))
    dx_principal_tipo_1 = st.selectbox("Diagnóstico Principal Reingreso (NUEVO/REPETIDO)", list(dx_principal_tipo_1_map.keys()))
    dx_principal_tipo_2 = st.selectbox("Diagnóstico Principal", list(dx_principal_tipo_2_map.keys()))

    ejecutar = st.form_submit_button("🔍 Predecir", use_container_width=True)

# -----------------------------------------------------
# PREDICCIÓN Y RESULTADO INTERACTIVO
# -----------------------------------------------------
if ejecutar:
    # preparar input
     # POP-UP DE ESPERA (modal)
    with st.spinner("Procesando predicción..."):        
        time.sleep(1)
    try:
        input_data = pd.DataFrame([{
            'nom_servicio_habilitado': map_servicio_habilitado[nom_servicio_habilitado],
            'edad': float(edad),
            'sexo': map_sexo[sexo],
            'regimen_afiliacion': map_regimen[regimen_afiliacion],
            'entidad_responsable_pago_validada': map_entidad_responsable[entidad_responsable_pago_validada],
            'clasificacion_1_triaje_enfermeria': map_triaje[clasificacion_1_triaje_enfermeria],
            'reclasificacion1_triaje_medico': map_triaje[reclasificacion1_triaje_medico],
            'urgencia_xpress_f3': map_urgencia_xpress[urgencia_xpress_f3],
            'servicio_ingreso': map_servicio_ingreso[servicio_ingreso],
            'ubicacion_triaje': map_ubicacion_triaje[ubicacion_triaje],
            'dx_principal_capitulo': dx_principal_capitulo_map[dx_principal_capitulo],
            'dx_principal_tipo_1': dx_principal_tipo_1_map[dx_principal_tipo_1],
            'dx_principal_tipo_2': dx_principal_tipo_2_map[dx_principal_tipo_2]
        }])
    except Exception as e:
        st.error(f"❌ Error al preparar los datos: {e}")
        st.stop()

    # mostrar los datos que se van a enviar (colapsable)
    with st.expander("Mostrar datos enviados al modelo", expanded=False):
        st.dataframe(input_data.T.rename(columns={0: "valor"}))

    # intentar obtener predicción y probabilidad (si aplica)
    try:
        pred = model.predict(input_data)[0]
    except Exception as e:
        st.error(f"❌ Error al ejecutar el modelo: {e}")
        st.stop()

    prob_text = None
    try:
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(input_data)
            # si binario: proba[0][1] es la probabilidad de clase positiva
            if proba.shape[1] == 2:
                prob = float(proba[0][1])
                prob_text = f"{prob*100:.1f}% probabilidad de permanencia"
            else:
                # multiclass: mostrar la clase predicha y su probabilidad
                prob = float(np.max(proba))
                prob_text = f"{prob*100:.1f}% confianza (clase {np.argmax(proba, axis=1)[0]})"
    except Exception:
        prob_text = None

    # mostrar resultado en dos columnas: tarjeta + explicación
    rcol1, rcol2 = st.columns([1, 2])

    with rcol1:
        # tarjeta visual
        if pred == 1:
            st.markdown(
                """
                <div style="border-radius:12px; padding:14px; background:linear-gradient(90deg,#fff0f0,#ffecec); border-left:6px solid #d32f2f;">
                    <h3 style="color:#c62828; margin:0;">🛑 Permanece en Urgencias</h3>
                    <p style="margin:4px 0 0 0; color:#6b6b6b;">El modelo estima que el paciente permanecerá en urgencias.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.image("https://cdn-icons-png.flaticon.com/512/5945/5945236.png", width=120)
        else:
            st.markdown(
                """
                <div style="border-radius:12px; padding:14px; background:linear-gradient(90deg,#f0fff4,#e7ffef); border-left:6px solid #2e7d32;">
                    <h3 style="color:#2e7d32; margin:0;">✅ Será dado de alta</h3>
                    <p style="margin:4px 0 0 0; color:#6b6b6b;">El modelo estima que el paciente será dado de alta.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.image("https://static.vecteezy.com/system/resources/thumbnails/067/404/599/small/3d-render-of-blue-exit-sign-with-person-walking-icon-directional-guidance-for-emergency-exits-and-free-png.png", width=120)

        if prob_text:
            st.metric(label="Confianza", value=prob_text)

    with rcol2:
        st.markdown("#### Explicación rápida")
        # Mostrar un texto sencillo; puedes personalizarlo para tu hospital
        if pred == 1:
            st.write(
                "- Priorizar observación y monitoreo.\n"
                "- Revisar recursos disponibles en la sala de urgencias.\n"
                "- Evaluar necesidad de ingreso o procedimientos."
            )
        else:
            st.write(
                "- Acompañar el alta con indicaciones de control y signos de alarma.\n"
                "- Se recomienda otorgar el alta con instrucciones de seguimiento.\n"
                "- En caso necesario, el médico puede decidir la hospitalización."
            )

        # botón para exportar resultado como CSV (descarga)
        result_df = input_data.copy()
        result_df["prediction"] = int(pred)
        if prob_text:
            result_df["confidence"] = prob_text

        csv = result_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Descargar entrada + predicción (CSV)", data=csv, file_name="prediccion_urgencia.csv", mime="text/csv")
        # Scroll a la tarjeta resultado (para UX) - usando st.experimental_rerun is heavy; mejor sugerir al usuario mirar abajo
        st.success("Predicción completada.")

    with st.container():
        st.markdown("""
            <style>
            .fade-in {
                animation: fadeIn 1.5s ease-in-out;
            }
            @keyframes fadeIn {
                0% {opacity: 0;}
                100% {opacity: 1;}
            }
            </style>
        """, unsafe_allow_html=True)

        if pred == 1:
            st.markdown("<h2 class='fade-in' style='color:red;'>🛑 El paciente se quedará en urgencias</h2>", unsafe_allow_html=True)
        else:
            st.markdown("<h2 class='fade-in' style='color:green;'>✅ El paciente será dado de alta</h2>", unsafe_allow_html=True)

# -----------------------------------------------------
# MINI DASHBOARD
# -----------------------------------------------------
st.markdown("---")
st.subheader("📊 Mini Dashboard del Modelo")

colA, colB, colC = st.columns(3)

with colA:
    st.metric("Variables usadas", "13")

with colB:
    st.metric("Tipo de modelo", "HistGradientBoostingClassifier")

with colC:
    st.metric("Clasificación", "Binaria (1 = Alta, 0 = Permanece)")

    
