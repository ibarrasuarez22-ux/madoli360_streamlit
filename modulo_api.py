import streamlit as st
import json
import datetime

def generar_respuesta_json():
    # 🔍 Trazabilidad por ID institucional
    params = st.query_params
    id_cliente = params.get("id_cliente", ["Desconocido"])[0]

    # 🕓 Timestamp institucional
    timestamp = datetime.datetime.now().isoformat()

    # 📘 Logging básico en pantalla (puede redirigirse a archivo si lo requiere)
    st.write(f"[{timestamp}] Consulta recibida de ID institucional: {id_cliente}")

    # 🎯 Estructura JSON alineada para Bubble o consumo API
    respuesta = {
        "status": "ok",
        "id_cliente": id_cliente,
        "timestamp": timestamp,
        "mensaje": "Parámetros recibidos correctamente.",
        "contenido": {
            "ejemplo": "Valor institucional",
            "siguiente_paso": "Validar en visualización"
        }
    }

    # 🚀 Mostrar en Streamlit y entregar como string JSON
    st.json(respuesta)
    return json.dumps(respuesta)
