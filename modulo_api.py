# modulo_api.py
import streamlit as st

def generar_respuesta_json():
    params = st.experimental_get_query_params()
    if "id_cliente" in params:
        id_cliente = params["id_cliente"][0]
        resultado = {
            "id_cliente": id_cliente,
            "promociones_sugeridas": [
                "Seguro Inteligente",
                "Bonificación por fidelidad",
                "Descuento territorial"
            ],
            "segmento": "auto",
            "estatus": "OK"
        }
        st.json(resultado)
        st.stop()
    else:
        st.warning("🟡 Parámetro 'id_cliente' no recibido.")
        st.stop()
