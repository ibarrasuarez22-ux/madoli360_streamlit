# ░ mod_json.py ░ Exportación Institucional JSON ░

import streamlit as st

def generar_respuesta_json(id_cliente, timestamp, mensaje, bitacora=None):
    respuesta = {
        "estado": "DE ACUERDO",
        "id_cliente": id_cliente,
        "marca_de_tiempo": timestamp,
        "mensaje": mensaje
    }

    st.subheader("📦 Exportación JSON")
    st.json(respuesta)

    if bitacora is not None:
        bitacora.append(f"✅ Respuesta JSON generada para cliente: {id_cliente}")
