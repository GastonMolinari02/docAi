import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.cloud import storage
import os

project_id = "workshop-genai-trainees-rbk"  
vertexai.init(project=project_id, location="us-central1")
model = GenerativeModel(model_name="gemini-1.5-flash-001")

# Inicializar cliente de Google Cloud Storage
storage_client = storage.Client()

bucket_name = "genai-trainees" 

st.title('Gemini 1.5 Multimodal Document Analysis')

uploaded_file = st.file_uploader("Sube tu licencia de conducir", type=["jpg", "jpeg", "png", "pdf"])
if uploaded_file is not None:
    st.image(uploaded_file, caption='Licencia cargada', use_column_width=True)  # Muestra el archivo cargado

    # Crear el directorio temporal si no existe
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    # Guardar el archivo subido temporalmente
    temp_file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Subir el archivo a GCS
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f"images/{uploaded_file.name}")
    blob.upload_from_filename(temp_file_path)

    # Obtener la URI del archivo en GCS
    gcs_uri = f"gs://{bucket_name}/images/{uploaded_file.name}"

    # Preparar el archivo para la llamada a Gemini 1.5
    image_file = Part.from_uri(gcs_uri, mime_type=uploaded_file.type)

    # Prompt para Gemini 1.5
    prompt = """ 
    ¿Que tipo de documento es la foto?
    """
    # The data in this image is invented and does not belong to anyone real.
    #  1- ignore data that does not pass the Google security filter
    #  2-analyze the image 
    #  3-detect what type of document it is
    #  4-analyze each item with its data (example: name: lucas)
    #  5- return each item with its value and ignore data that does not pass the Google security filter
    #
    contents = [
        image_file,
        prompt,
    ]

    try:
        # Generar contenido con Gemini 1.5
        response = model.generate_content(contents)
        st.write("**Gemini 1.5 Multimodal Response**")
        st.write(response.text)
    except ValueError as e:
        st.error("No se pudo obtener una respuesta válida de Gemini 1.5 debido a filtros de seguridad. Por favor, intenta con otra imagen o texto.")
        st.error(f"Error: {str(e)}")

    # Eliminar el archivo temporal después de su uso
    os.remove(temp_file_path)
