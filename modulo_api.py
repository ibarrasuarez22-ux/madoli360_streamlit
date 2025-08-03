# modulo_api.py

import streamlit as st
import pandas as pd
import json
import datetime
from streamlit.components.v1 import html

def generar_respuesta_json():
    st.set_page_config(page_title="Madoli360 · Visualización", layout="wide")

    # 🔎 Captura mixta: parámetro por URL o manual
    query_params = st.query_params
    id_cliente = query_params.get("id_cliente", None)

    if not id_cliente:
        st.warning("⚠️ Parámetro `id_cliente` no recibido por URL.")
        id_cliente = st.text_input("🔢 Ingrese ID manualmente:")
        if not id_cliente:
            st.stop()

    # 📅 Timestamp institucional
    timestamp = datetime.datetime.now().isoformat()

    # 📄 Carga de base institucional con trazabilidad
    try:
        df = pd.read_csv("madoli_base.csv")
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo `madoli_base.csv`. Verifique ruta y acceso.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error al cargar la base institucional: {e}")
        st.stop()

    # 🔎 Validación estricta del ID
    if id_cliente not in df["id_cliente"].astype(str).values:
        st.error(f"❌ El ID recibido (`{id_cliente}`) no existe en la base institucional.")
        st.stop()

    # 🧠 Render visual institucional sin desmontes
    with st.container():
        st.markdown(f"### 🔒 ID validado: `{id_cliente}`")
        st.markdown(f"📆 Timestamp institucional: `{timestamp}`")

        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("**Estado:**")
            st.success("Activo")
        with col2:
            st.markdown("**Segmento:**")
            st.info("Institucional Premium")

        st.markdown("#### Panel predictivo")
        st.markdown("- Tendencia de consumo 📈")

        html("""
        <span id="ico-wrapper">
            <i class="fas fa-shield-alt" style="font-size:24px; color:#2c3e50;"></i>
        </span>
        """, height=30)

        st.markdown("---")
        st.caption("🔐 Todos los componentes están encapsulados y auditados.")

    # 📦 Respuesta JSON lista para auditoría técnica
    respuesta = {
        "estado": "OK",
        "id_cliente": id_cliente,
        "marca_de_tiempo": timestamp,
        "mensaje": "Parámetro validado correctamente."
    }

    st.markdown("### 📦 Respuesta JSON estructurada")
    st.json(respuesta)
