import streamlit as st
import requests
import json
import base64
import os
from google.auth.transport.requests import Request
from google.oauth2.id_token import fetch_id_token

# Configurar la variable de entorno en el script
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "{Path de tu credential.json}"

LOCAL = False  # Cambia a False cuando pruebes en la nube
ENDPOINT_URL = "{Url de tu endpoint}"

# Verifica la variable de entorno
if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
    raise EnvironmentError("La variable de entorno GOOGLE_APPLICATION_CREDENTIALS no está configurada.")

# Obtener el token de identidad
def get_id_token():
    auth_req = Request()
    id_token = fetch_id_token(auth_req, ENDPOINT_URL)
    return id_token

if not LOCAL:
    id_token = get_id_token()

url = (
    ENDPOINT_URL
    if not LOCAL
    else "http://localhost:8080"
)

st.title('DocumentAi')

uploaded_file = st.file_uploader("Sube tu licencia de conducir", type=["jpg", "jpeg", "png", "pdf"])
if uploaded_file is not None:
    # Dividir la página en dos columnas
    col1, col2 = st.columns([1, 2])

    with col1:
        # Muestra la imagen del documento
        st.image(uploaded_file, caption='Licencia cargada', use_column_width=True)

    with col2:
        # Leer el archivo subido y codificarlo en base64(es necesario para setear la respuesta)
        encoded_string = base64.b64encode(uploaded_file.read()).decode('utf-8')

        # Autenticación con header
        headers = {"Authorization": f"Bearer {id_token}"} if not LOCAL else {}

        # Enviar el archivo a la Cloud Function
        ret = requests.post(
            url,
            json={"img": encoded_string},
            headers=headers,
        )

        if ret.status_code == 200:
            result = ret.json()
            if 'error' in result:
                st.write(f"Error en la respuesta: {result['error']}")
            else:
                # Crear tres columnas
                col2_1, col2_2, col2_3 = st.columns(3)

                with col2_1:
                    st.write("### Geminis Response")
                    for key, value in result['gemini_response'].items():
                        st.write(f"**{key}**: {value}")
                with col2_2:
                    st.write("### US Driver License Response")
                    for key, value in result['driver_response'].items():
                        st.write(f"**{key}**: {value}")
                with col2_3:
                    st.write("### Proofing Response")
                    for key, value in result['proofing_response'].items():
                        st.write(f"**{key}**: {value}")

                
        else:
            st.write(f"Error: {ret.status_code} - {ret.text}")
