import streamlit as st
import requests
import json

st.title('DocumentAi')

uploaded_file = st.file_uploader("Sube tu licencia de conducir", type=["jpg", "jpeg", "png", "pdf"])
if uploaded_file is not None:
    st.image(uploaded_file, caption='Licencia cargada', use_column_width=True)#muestra el archivo cargado
    files = {"file": uploaded_file.getvalue()}# convierte el archivo a un formato que pueda ser enviado a la Cloud Function

    url = "URL de la Cloud Function desplegada"
    
    
    response = requests.post(url, files=files) # llamar a la Cloud Function

    if response.status_code == 200:
        result = response.json()
        st.write("Texto extraído:")
        st.write(result["text"])
    else:
        st.write("Error")