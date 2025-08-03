import streamlit as st
import json
import datetime
import pandas as pd
from streamlit.components.v1 import html

# 🔒 Layout institucional encapsulado
def render_layout_blindado(id_cliente):
    with st.container():
        st.markdown(f"### 🧾 Cliente institucional: `{id_cliente}`")

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
        st.markdown("Información adicional cargada dinámicamente…")
        st.caption("🔐 Layout auditado. Todos los componentes están encapsulados.")

# 🧪 Validación URL + respuesta JSON trazable
def generar_respuesta_json():
    # 📦 Parámetro recibido vía URL
    query_params = st.query_params
    id_cliente = query_params.get("id_cliente", "Desconocido")

    # 📆 Timestamp institucional
    timestamp = datetime.datetime.now().isoformat()

    # 🔍 Visualización del parámetro recibido
    st.markdown("### 🧪 Parámetro recibido")
    st.write(f"🔍 ID recibido por URL: `{id_cliente}`")
    st.write(f"📆 Timestamp institucional: `{timestamp}`")

    # 📄 Cargar base institucional
    try:
        df = pd.read_csv("madoli_base.csv")
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo `madoli_base.csv`. Verifique la ruta.")
        return
    except Exception as e:
        st.error(f"❌ Error al cargar la base institucional: {e}")
        return

    # 🔍 Validación de existencia del ID
    if id_cliente not in df["id_cliente"].astype(str).values:
        st.error(f"❌ El parámetro recibido ('{id_cliente}') no coincide con ningún ID válido en la base institucional.")
        return

    # 🖥️ Render visual encapsulado
    render_layout_blindado(id_cliente)

    # 📦 Respuesta JSON limpia y sin sección "contenido"
    respuesta = {
        "estado": "OK",
        "id_cliente": id_cliente,
        "marca de tiempo": timestamp,
        "mensaje": "Parámetro validado correctamente."
    }

    # 🔐 Visualización final
    st.markdown("### 🔐 Diseño auditado. Todos los componentes están encapsulados.")
    st.json(respuesta)

    return json.dumps(respuesta)
