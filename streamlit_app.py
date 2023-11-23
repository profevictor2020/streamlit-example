import streamlit as st
from openai import OpenAI
import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Usa os.environ para obtener el valor de la clave de API de OpenAI
openai_api_key = os.environ.get('OPENAI_API_KEY')
external_endpoint_url = os.environ.get('EXTERNAL_ENDPOINT_URL')

# Configuración de OpenAI (asegúrate de tener configurada tu clave de API de OpenAI)
client = OpenAI(api_key=openai_api_key)

def get_data_from_endpoint(IdCentro, Fecha, Hora):
    # Parámetros para la solicitud al endpoint externo
    try:
        response = requests.get(
            external_endpoint_url,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            params={'IdCentro': IdCentro, 'Fecha': Fecha, 'Hora': Hora}
        )

        # Verificar si la solicitud fue exitosa
        response.raise_for_status()

        # Parsear la respuesta JSON u otro formato según lo que retorne el endpoint
        result = response.json()  # Ajusta esto según el formato real de la respuesta
        return result
    except requests.exceptions.RequestException as e:
        return f"Error: No se pudo obtener datos del endpoint. Detalles: {str(e)}"

# Funciones disponibles para OpenAI
available_functions = {
    "get_data_from_endpoint": get_data_from_endpoint,
}

# Definición de funciones para OpenAI
functions = [
    {
        "name": "get_data_from_endpoint",
        "description": '''Debes considerar para la funcion get_data_from_endpoint(IdCentro, Fecha, Hora) 
                       los siguientes parámetros: IdCentro, Fecha, Hora.
                       Debes extraer el centro,  la fecha y hora de consulta.
                       La fecha debes pasarla con el siguiente formato:
                       por ejemplo si es 21 de noviembre 2023 debe ser 20231121
                       La hora debes pasarla como entero
                       por ejemplo 14:00 debes pasar el parametro como 14.
                       El centro Chauques esta asociado con el IdCentro AQ008, 
                       Teguel 3 con el IdCentro AQ010, Centro Chidguapi con el IdCentro AQ003,
                       Centro Guar con el IdCentro AQ004, Detif con el IdCentro AQ011,
                       Ensenada Queten con el IdCentro AQ005. Tienes que dar prioridad a los sensores''',
        "parameters": {
            "type": "object",
            "properties": {
                "IdCentro": {"type": "string", "description": "IdCentro."},
                "Fecha": {"type": "string", "description": "Date."},
                "Hora": {"type": "string", "description": "Time."},
            },
            "required": ["IdCentro", "Fecha", "Hora"],
        },
    }
]

# Inicia la aplicación Streamlit
st.title("Asistente de Centro de Salmones")

# Solicitar información al usuario
query = st.text_input("¿Qué información necesitas?")
if query:
    # Obtener respuesta de OpenAI
    messages = [{"role": "user", "content": query}]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        functions=functions,
        function_call="auto",
    )

    # Ejecutar la función de OpenAI
    function_name = response.choices[0].message.function_call.name
    arguments = response.choices[0].message.function_call.arguments
    function_response = get_data_from_endpoint(**json.loads(arguments))

    # Presentar la respuesta de la función de OpenAI
    st.json(function_response)
