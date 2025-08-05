# -*- coding: utf-8 -*-
"""
Madoli360 · Plataforma Institucional
Autor: CCPI S.A.S. de C.V.
Versión: 1.0.0 · Fecha de despliegue: 2025-08-03
"""
import os
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from mod_json import generar_respuesta_json
from datetime import datetime
from google.cloud import bigquery

# === CONFIGURACIÓN INICIAL ===
st.set_page_config(page_title="Madoli360", layout="wide")
bitacora = []
RUTA_DATOS = "/Users/robertoibarrasuarez/Desktop/homologación_madoli/"
CREDENCIALES_BIGQUERY = "/Users/robertoibarrasuarez/Desktop/credenciales_gcp.json"

# === PARÁMETROS BUBBLE ===
query_params = st.query_params
id_cliente_url = query_params.get("id_cliente", [None])[0]

# === LOGOS INSTITUCIONALES ===
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    try:
        st.image("madoli_logo.png", width=100)
    except:
        st.warning("No se encontró madoli_logo.png")

with col_titulo:
    st.markdown("## 🛡️ Madoli360 – Inteligencia Institucional Predictiva")

# === FUNCIÓN GENERAL PARA CARGA DE BASES ===
def cargar_base(nombre_archivo):
    path_local = os.path.join(RUTA_DATOS, nombre_archivo)
    URL_GITHUB_BASE = "https://raw.githubusercontent.com/ibarrasuarez22-ux/madoli360_streamlit/main/"
    ruta_github = URL_GITHUB_BASE + nombre_archivo

    try:
        df = pd.read_csv(path_local, encoding="utf-8")
        bitacora.append(f"[{datetime.now()}] {nombre_archivo} cargado localmente ({len(df):,} registros)")
        return df
    except:
        bitacora.append(f"[{datetime.now()}] {nombre_archivo} no encontrado en local. Intentando GitHub...")
        try:
            df = pd.read_csv(ruta_github, encoding="utf-8")
            bitacora.append(f"[{datetime.now()}] {nombre_archivo} cargado desde GitHub ({len(df):,} registros)")
            return df
        except Exception as e:
            bitacora.append(f"[{datetime.now()}] ERROR carga {nombre_archivo}: {str(e)}")
            return pd.DataFrame()

# === CARGA DE BASES CLAVE ===
df_base = cargar_base("madoli_base.csv")
df_denue = cargar_base("denue.csv")
df_ventas = cargar_base("ventas_sectoriales.csv")

# === VALIDACIÓN SILENCIOSA CON LOG INSTITUCIONAL ===
if df_base.empty:
    bitacora.append(f"[{datetime.now()}] ERROR carga madoli_base.csv: base vacía")

if df_denue.empty:
    bitacora.append(f"[{datetime.now()}] ERROR carga denue.csv: base vacía")

if df_ventas.empty:
    bitacora.append(f"[{datetime.now()}] ERROR carga ventas_sectoriales.csv: base vacía")

# === CARGA DE BASES ===
def cargar_base(nombre_archivo):
    # Ruta local
    path_local = os.path.join(RUTA_DATOS, nombre_archivo)

    # Ruta GitHub
    URL_GITHUB_BASE = "https://raw.githubusercontent.com/ibarrasuarez22-ux/madoli360_streamlit/main/data/"
    ruta_github = URL_GITHUB_BASE + nombre_archivo

    # Intento local primero
    try:
        return pd.read_csv(path_local, encoding="utf-8")
    except:
        st.warning(f"⚠️ No se encontró {nombre_archivo} en local, intentando carga desde GitHub...")
        try:
            return pd.read_csv(ruta_github, encoding="utf-8")
        except Exception as e:
            st.error(f"⛔ Fallo doble en carga de {nombre_archivo}: {str(e)}")
            return pd.DataFrame()

# === INGESTA CENSO INEGI DESDE GCS (PÚBLICO) ===

URL_CENSO_PUBLICO = "https://storage.googleapis.com/madoli360-archivos/censo_inegi.csv"

def cargar_censo_desde_gcs(url_csv: str) -> pd.DataFrame:
    try:
        df_censo = pd.read_csv(url_csv, encoding="utf-8")
        bitacora.append(f"[{datetime.now()}] Censo INEGI cargado correctamente ({len(df_censo):,} registros)")
        return df_censo
    except Exception as e:
        bitacora.append(f"[{datetime.now()}] ERROR carga Censo INEGI: {str(e)}")
        return pd.DataFrame()

@st.cache_data(show_spinner="🔄 Cargando Censo INEGI desde GCS...")
def cargar_censo_cacheada(url_csv: str) -> pd.DataFrame:
    return cargar_censo_desde_gcs(url_csv)

# Carga institucional
df_censo = cargar_censo_cacheada(URL_CENSO_PUBLICO)

# Registro en bitácora (ya fuera de caché)
if 'bitacora' in globals():
    if df_censo.empty:
        bitacora.append("⚠️ df_censo vacío tras intento de carga desde GCS.")
    else:
        bitacora.append(f"✅ Censo INEGI disponible ({df_censo.shape[0]:,} registros)")

# === NORMALIZACIÓN Y HOMOLOGACIÓN ===
bitacora = []

for col in ['start_date', 'end_date', 'birth_date']:
    if col in df_base.columns:
        df_base[col] = pd.to_datetime(df_base[col], errors='coerce')
        bitacora.append(f"✔️ Normalizada columna: {col}")

for campo in ['Ramo', 'Subramo', 'product']:
    if campo in df_base.columns:
        df_base[campo] = df_base[campo].astype(str).str.strip().str.upper()

mapa_ramos = {
    'AUTO': 'AUTOS', 'AUTOS PARTICULAR': 'AUTOS', 'CAMIONES': 'AUTOS',
    'BENEFICIOS': 'BENEFICIOS', 'DAÑOS': 'DAÑOS', 'GMM': 'GMM', 'HOGAR': 'HOGAR',
    'PMM': 'PMM', 'SALUD': 'SALUD', 'VDA': 'VIDA', 'VIDA': 'VIDA'
}
mapa_subramos = {
    'ACCIDENTES': 'ACCIDENTES', 'AUTOS PARTICULAR': 'AUTOS', 'CAMIONES': 'AUTOS',
    'GMM INDIVIDUAL / FAMILIA': 'GMM', 'GERENTE GENERAL': 'GERENCIA',
    'RC': 'RESPONSABILIDAD CIVIL', 'RESPONSABILIDAD CIVIL': 'RESPONSABILIDAD CIVIL',
    'HOGAR': 'HOGAR', 'YAYA': 'YAYA', 'EDUCATIVO': 'EDUCATIVO',
    'EMPRESARIAL': 'EMPRESARIAL', 'SALUD': 'SALUD', 'VIDA': 'VIDA'
}
df_base['Ramo'] = df_base['Ramo'].replace(mapa_ramos)
df_base['Subramo'] = df_base['Subramo'].replace(mapa_subramos)

bitacora.append("✔️ Homologación de Ramo y Subramo aplicada")

# === TABS INSTITUCIONALES ===
tabs = st.tabs([
    "📊 KPIs Generales", "🗂️ Perfil por Cliente", "🌎 Territorial",
    "🏢 Sectorial", "🧠 IA Predictiva", "📜 Bitácora Técnica"
])
# === 📊 KPIs Generales ===
with tabs[0]:
    st.header("📈 Panel Estratégico de Pólizas")

    # Homologación aseguradora
    col_aseguradora = "source" if "source" in df_base.columns else ("aseguradora" if "aseguradora" in df_base.columns else None)
    col_product = None

    # Homologación de columna 'product'
    for posible in ["product", "producto", "nombre_producto", "tipo_producto"]:
        if posible in df_base.columns:
            col_product = posible
            bitacora.append(f"✅ Columna homologada para 'Producto': '{posible}'")
            break

    if not col_product:
        bitacora.append("⚠️ Columna 'product' no encontrada. Filtro omitido.")

    # Filtros dinámicos
    filtros = {
        "Aseguradora": sorted(df_base[col_aseguradora].dropna().unique()) if col_aseguradora else [],
        "Producto": sorted(df_base[col_product].dropna().unique()) if col_product else [],
        "Ramo": sorted(df_base['Ramo'].dropna().unique()) if 'Ramo' in df_base.columns else [],
        "Subramo": sorted(df_base['Subramo'].dropna().unique()) if 'Subramo' in df_base.columns else []
    }

    seleccion = {
        clave: st.sidebar.multiselect(clave, valores, default=valores)
        for clave, valores in filtros.items()
    }

    # Aplicación de filtros
    condiciones = (
        df_base[col_aseguradora].isin(seleccion['Aseguradora']) if col_aseguradora else True
    ) & (
        df_base[col_product].isin(seleccion['Producto']) if col_product else True
    ) & (
        df_base['Ramo'].isin(seleccion['Ramo']) if 'Ramo' in df_base.columns else True
    ) & (
        df_base['Subramo'].isin(seleccion['Subramo']) if 'Subramo' in df_base.columns else True
    )

    df_kpi = df_base[condiciones].copy()

    # Validación de 'premium_mxn'
    if 'premium_mxn' in df_kpi.columns:
        df_kpi['premium_mxn'] = pd.to_numeric(df_kpi['premium_mxn'], errors='coerce')
        df_kpi = df_kpi[df_kpi['premium_mxn'] > 0]
        bitacora.append("✅ Validación de 'premium_mxn': valores positivos y numéricos")

    # Métricas y gráficos
    if df_kpi.empty:
        st.warning("⚠️ No se encontraron pólizas con los filtros aplicados.")
    else:
        col1, col2, col3, col4, col5 = st.columns(5)

        if 'policy_number' in df_kpi.columns:
            col1.metric("📄 Pólizas", f"{df_kpi['policy_number'].nunique():,}")
        else:
            col1.metric("📄 Pólizas", "Columna no disponible")
            bitacora.append("⚠️ Columna 'policy_number' no presente en vista KPIs")

        col2.metric("👥 Clientes", f"{df_kpi['id_cliente'].nunique():,}" if 'id_cliente' in df_kpi.columns else "N/D")
        col3.metric("🏢 Aseguradoras", f"{df_kpi[col_aseguradora].nunique():,}" if col_aseguradora in df_kpi.columns else "N/D")
        col4.metric("🧾 Productos", f"{df_kpi[col_product].nunique():,}" if col_product in df_kpi.columns else "N/D")
        col5.metric("💰 Prima total MXN", f"${df_kpi['premium_mxn'].sum():,.2f}" if 'premium_mxn' in df_kpi.columns else "$0.00")

        st.subheader("📊 Distribución del Portafolio")

        # Gráficos solo si columnas existen
        if col_aseguradora and col_aseguradora in df_kpi.columns:
            graf1 = alt.Chart(df_kpi).mark_bar().encode(
                x='count()', y=col_aseguradora, color=col_aseguradora
            ).properties(height=300)
            st.altair_chart(graf1, use_container_width=True)

        if col_product and col_product in df_kpi.columns:
            graf2 = alt.Chart(df_kpi).mark_bar().encode(
                x='count()', y=col_product, color=col_product
            ).properties(height=300)
            st.altair_chart(graf2, use_container_width=True)
   

# === 🗂️ Perfil por Cliente ===
with tabs[1]:
    st.title("🧑‍💼 Perfil por Cliente – Madoli360")

    if 'id_cliente' not in df_base.columns:
        st.error("⛔ La base no contiene la columna 'id_cliente'")
    else:
        if id_cliente_url:
            id_seleccionado = id_cliente_url
            st.success(f"ID cliente recibido desde Bubble: `{id_seleccionado}`")
        else:
            id_seleccionado = st.selectbox("Seleccionar cliente (ID)", sorted(df_base['id_cliente'].dropna().unique()))

        perfil_df = df_base[df_base['id_cliente'] == id_seleccionado].copy()

        if perfil_df.empty:
            st.warning("⚠️ No se encontraron pólizas asociadas.")
        else:
            nombre = perfil_df['contractor_name'].dropna().iloc[0] if 'contractor_name' in perfil_df.columns else "Sin nombre"
            st.markdown(f"### 👤 Contratante: `{nombre}`")

            # Validación de prima
            if 'premium_mxn' in perfil_df.columns:
                perfil_df['premium_mxn'] = pd.to_numeric(perfil_df['premium_mxn'], errors='coerce')
                perfil_df = perfil_df[perfil_df['premium_mxn'] > 0]

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📄 Pólizas", f"{perfil_df.shape[0]}")
            col2.metric("🏢 Aseguradoras", f"{perfil_df['source'].nunique() if 'source' in perfil_df.columns else 0}")
            col3.metric("🧾 Productos", f"{perfil_df['product'].nunique() if 'product' in perfil_df.columns else 0}")
            col4.metric("💰 Prima total MXN", f"${perfil_df['premium_mxn'].sum():,.2f}" if 'premium_mxn' in perfil_df.columns else "$0.00")

            st.subheader("🧠 Score Institucional")
            total_p = perfil_df.shape[0]
            diversidad = perfil_df['product'].nunique() if 'product' in perfil_df.columns else 0
            vencimientos = perfil_df['end_date'].notna().sum() if 'end_date' in perfil_df.columns else 0
            retencion_score = ((total_p * 0.5) + (diversidad * 0.3) + (vencimientos * 0.2)) / 10

            clasificacion = "En riesgo"
            if retencion_score >= 7:
                clasificacion = "Prioritario"
            elif retencion_score >= 4:
                clasificacion = "Promotor"

            colr1, colr2 = st.columns([1, 3])
            colr1.metric("🔄 Score Retención", f"{retencion_score:.2f}")
            colr2.markdown(f"**Clasificación institucional:** `{clasificacion}`")

            bitacora.append(f"✅ Perfil cliente desplegado: {id_seleccionado} con score {retencion_score:.2f}")

# === 🌎 Territorial ===
with tabs[2]:
    st.title("🌎 Módulo Territorial")

    if df_censo.empty or df_denue.empty:
        st.warning("⚠️ No se encontraron bases censales o empresariales.")
        bitacora.append("⚠️ Bases censales o DENUE no disponibles para módulo territorial.")
    else:
        # 🔄 Renombrado institucional para compatibilidad
        if 'latitud' in df_denue.columns and 'longitud' in df_denue.columns:
            df_denue = df_denue.rename(columns={'latitud': 'latitude', 'longitud': 'longitude'})
            bitacora.append("✅ Coordenadas renombradas para st.map")

        if 'nombre_empresa' in df_denue.columns:
            df_denue = df_denue.rename(columns={'nombre_empresa': 'nombre'})
            bitacora.append("✅ Columna 'nombre_empresa' renombrada a 'nombre'")

        if 'giro' not in df_denue.columns:
            posibles_giro = ['actividad', 'rama', 'C√≥digo de la clase de actividad SCIAN']
            for p in posibles_giro:
                if p in df_denue.columns:
                    df_denue = df_denue.rename(columns={p: 'giro'})
                    bitacora.append(f"✅ Columna '{p}' renombrada a 'giro'")
                    break

        # 📬 Renombres adicionales para dirección y correo
        renombres_adicionales = {
            'domicilio': 'direccion',
            'direccion_empresa': 'direccion',
            'correo': 'correo_electronico',
            'email': 'correo_electronico'
        }

        for col_orig, col_nueva in renombres_adicionales.items():
            if col_orig in df_denue.columns and col_nueva not in df_denue.columns:
                df_denue = df_denue.rename(columns={col_orig: col_nueva})
                bitacora.append(f"✅ Columna '{col_orig}' renombrada a '{col_nueva}'")

        # 🧩 Homologación columna municipio
        col_municipio_censo = None
        for posible in ["municipio", "nombre_municipio", "nom_mun", "localidad"]:
            if posible in df_censo.columns:
                col_municipio_censo = posible
                bitacora.append(f"✅ Columna censal homologada: '{posible}'")
                break

        col_municipio_denue = "municipio" if "municipio" in df_denue.columns else None
        if col_municipio_denue:
            bitacora.append("✅ Columna DENUE reconocida como 'municipio'")
        else:
            bitacora.append("⚠️ Columna 'municipio' no presente en df_denue")

        # 🧼 Normalización territorial
        if col_municipio_censo:
            df_censo[col_municipio_censo] = df_censo[col_municipio_censo].astype(str).str.upper()
        if col_municipio_denue:
            df_denue[col_municipio_denue] = df_denue[col_municipio_denue].astype(str).str.upper()
        if 'giro' in df_denue.columns:
            df_denue['giro'] = df_denue['giro'].astype(str).str.upper()

        # 🗺️ Activación selector de municipio
        if col_municipio_censo and col_municipio_denue:
            municipios = sorted(df_denue[col_municipio_denue].dropna().unique())
            municipio_sel = st.selectbox("Seleccionar municipio", municipios)

            df_mun_censo = df_censo[df_censo[col_municipio_censo] == municipio_sel]
            df_mun_denue = df_denue[df_denue[col_municipio_denue] == municipio_sel]

            st.subheader(f"📍 Empresas registradas en {municipio_sel}")
            cols_denue_vis = ['nombre', 'giro', 'latitude', 'longitude', 'direccion', 'correo_electronico']

            faltantes = [col for col in cols_denue_vis if col not in df_mun_denue.columns]
            if not faltantes:
                st.dataframe(df_mun_denue[cols_denue_vis])
                bitacora.append(f"✅ Tabla completa desplegada para '{municipio_sel}'")
            else:
                st.warning(f"⚠️ Faltan columnas clave para despliegue completo: {faltantes}")
                bitacora.append(f"⚠️ Visualización incompleta para '{municipio_sel}': {faltantes}")

            # 📦 Descarga institucional
            st.download_button(
                label=f"📁 Descargar empresas de {municipio_sel} en CSV",
                data=df_mun_denue.to_csv(index=False).encode('utf-8'),
                file_name=f"empresas_{municipio_sel}.csv",
                mime='text/csv'
            )
            bitacora.append(f"✅ Botón de descarga activado para '{municipio_sel}'")

            st.subheader(f"📊 Indicadores censales de {municipio_sel}")
            st.dataframe(df_mun_censo)

            if 'latitude' in df_mun_denue.columns and 'longitude' in df_mun_denue.columns:
                st.map(df_mun_denue[['latitude', 'longitude']].dropna())
                bitacora.append(f"✅ Mapa desplegado para municipio '{municipio_sel}'")
            else:
                st.info("ℹ️ Coordenadas no disponibles para mapeo DENUE.")
                bitacora.append(f"ℹ️ Mapa omitido por falta de coordenadas en '{municipio_sel}'")
        else:
            st.warning("⚠️ No se pudo homologar 'municipio' en ambas bases.")
            bitacora.append("⚠️ Homologación de 'municipio' fallida entre censo y DENUE")

# === 🏢 Sectorial ===
with tabs[3]:
    st.title("🏢 Módulo Sectorial")

    if df_ventas.empty:
        st.warning("⚠️ No se encontró base de ventas.")
        bitacora.append("⚠️ Base 'ventas_sectoriales.csv' vacía o no cargada.")
    else:
        # 📅 Conversión de fechas y cálculo de trimestre
        if 'fecha' in df_ventas.columns:
            try:
                df_ventas['fecha'] = pd.to_datetime(df_ventas['fecha'], errors='coerce')
                df_ventas = df_ventas.dropna(subset=['fecha'])
                df_ventas['trimestre'] = df_ventas['fecha'].dt.to_period('Q').astype(str)
                bitacora.append("✅ Fechas convertidas y trimestres calculados.")
            except Exception as e:
                st.error(f"❌ Error al procesar fechas: {e}")
                bitacora.append(f"❌ Error en conversión de fechas: {e}")
        else:
            st.warning("⚠️ Columna 'fecha' no encontrada.")
            bitacora.append("⚠️ Columna 'fecha' ausente en base de ventas.")

        # 🧩 Homologación de columna 'Ramo'
        col_ramo_ventas = None
        for posible in ["Ramo", "ramo", "tipo_ramo", "segmento_ramo"]:
            if posible in df_ventas.columns:
                col_ramo_ventas = posible
                df_ventas[posible] = df_ventas[posible].astype(str).str.upper()
                bitacora.append(f"✅ Columna homologada para 'Ramo': '{posible}'")
                break

        # 📊 Visualización por trimestre y aseguradora
        if col_ramo_ventas and all(col in df_ventas.columns for col in ['Ventas', 'nombre', 'trimestre']):
            ramo_sel = st.selectbox("Seleccionar ramo", sorted(df_ventas[col_ramo_ventas].dropna().unique()))
            df_ramo = df_ventas[df_ventas[col_ramo_ventas] == ramo_sel]

            df_trimestral = df_ramo.groupby(['nombre', 'trimestre'])['Ventas'].sum().reset_index()
            df_trimestral['Ventas'] = df_trimestral['Ventas'].round(2)

            st.subheader("📊 Ventas Trimestrales por Aseguradora")
            fig = px.bar(
                df_trimestral,
                x='trimestre',
                y='Ventas',
                color='nombre',
                text='Ventas',
                barmode='group',
                labels={'trimestre': 'Trimestre', 'Ventas': 'Ventas Totales', 'nombre': 'Aseguradora'},
                title=f"Ventas por Trimestre – {ramo_sel}"
            )
            fig.update_layout(xaxis_title="Trimestre", yaxis_title="Ventas", legend_title="Aseguradora")
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
            bitacora.append("✅ Gráfico de ventas trimestrales desplegado.")
        else:
            st.warning("⚠️ Columnas clave faltantes para graficar por trimestre.")
            bitacora.append("⚠️ No se pudo graficar ventas por aseguradora y trimestre.")

# === 🧠 IA Predictiva ===
with tabs[4]:
    st.title("🧠 IA Predictiva – Clustering Institucional")

    if df_base.empty or 'id_cliente' not in df_base.columns or 'contractor_name' not in df_base.columns:
        st.warning("⚠️ No se puede aplicar clustering por falta de columnas clave.")
        bitacora.append("⚠️ Clustering omitido por ausencia de 'id_cliente' o 'contractor_name'.")
    else:
        # 🧩 Preparación de datos
        df_cluster = df_base[['id_cliente', 'contractor_name']].dropna()

        # 🔢 Codificación categórica
        df_cluster['id_cliente_encoded'] = df_cluster['id_cliente'].astype('category').cat.codes
        df_cluster['contractor_encoded'] = df_cluster['contractor_name'].astype('category').cat.codes

        # 🧠 Clustering KMeans
        from sklearn.cluster import KMeans
        X = df_cluster[['id_cliente_encoded', 'contractor_encoded']]
        kmeans = KMeans(n_clusters=3, random_state=42).fit(X)
        df_cluster['cluster'] = kmeans.labels_

        # 📊 Visualización de distribución
        st.subheader("📊 Distribución por cluster")
        import altair as alt
        graf_cluster = alt.Chart(df_cluster).mark_bar().encode(
            x='count()', y='cluster:N', color='cluster:N'
        ).properties(height=300)
        st.altair_chart(graf_cluster, use_container_width=True)
        bitacora.append("✅ Clustering por cliente y contratante ejecutado.")

        # 📋 Tabla de clientes clasificados
        st.subheader("📋 Clientes clasificados por cluster")
        st.dataframe(df_cluster[['id_cliente', 'contractor_name', 'cluster']].sort_values(by='cluster'))

        # 📁 Descarga CSV institucional
        st.download_button(
            label="📁 Descargar clasificación por cluster (CSV)",
            data=df_cluster[['id_cliente', 'contractor_name', 'cluster']].to_csv(index=False).encode('utf-8'),
            file_name="clientes_clusterizados.csv",
            mime="text/csv"
        )
        bitacora.append("✅ Botón de descarga CSV activado para clustering por cliente.")

        # 🔄 Consolidación de clientes por cluster
        fuentes = []
        for _, row in df_cluster.iterrows():
            fuentes.append({
                "id_cliente": row["id_cliente"],
                "segmento": str(row["cluster"]),
                "historial": []  # 🔁 puede integrarse desde otro módulo si aplica
            })

        # 🧠 Generación por botón
        st.subheader("🎯 Promociones predictivas por cliente clasificado")
        if st.button("🧠 Generar promociones predictivas"):
            from modulo_promociones import generar_promociones_consolidadas
            resultados_promos = generar_promociones_consolidadas(fuentes, bitacora)

            # 👁️ Visualización de resultados
            st.markdown("### 🔍 Resultados de promociones sugeridas")
            for r in resultados_promos:
                if "error" not in r:
                    st.markdown(f"- ✅ `{r['id_cliente']}` → {', '.join(r['promociones_sugeridas'])}")
                else:
                    st.warning(f"⚠️ Cliente `{r['id_cliente']}`: {r['error']}")

            # 📤 Envío automático a Bubble
            if st.button("📤 Enviar promociones a Bubble"):
                import requests
                enviados = 0
                for r in resultados_promos:
                    if "error" not in r:
                        payload = {
                            "id_cliente": r["id_cliente"],
                            "promociones_sugeridas": r["promociones_sugeridas"]
                        }
                        response = requests.post(
                            "https://madoli360.bubbleapps.io/api/1.1/wf/actualizar_cliente",
                            json=payload
                        )
                        if response.status_code == 200:
                            enviados += 1
                        else:
                            st.error(f"❌ Falla para `{r['id_cliente']}` | {response.status_code}")

                st.success(f"📬 {enviados} promociones enviadas exitosamente a Bubble.")
                bitacora.append(f"📤 {enviados} promociones enviadas a Bubble vía Streamlit.")

## === 📜 Bitácora Técnica ===
with tabs[5]:
    st.title("📜 Bitácora Técnica")
    st.markdown("### 🧾 Log institucional de carga y homologación")

    # Mostrar bitácora acumulada
    if bitacora:
        for entrada in bitacora:
            st.markdown(f"- {entrada}")
    else:
        st.info("ℹ️ No se han registrado eventos en la bitácora técnica.")

    # Validación estructural de columnas obligatorias
    columnas_obligatorias = ['policy_number', 'id_cliente', col_product, 'Ramo', 'Subramo', 'premium_mxn']
    columnas_faltantes = []

    for posible in columnas_obligatorias:
        if posible and posible in df_base.columns:
            bitacora.append(f"✅ Columna presente: '{posible}'")
        else:
            msg = f"⚠️ Falta columna: {posible}" if posible else "⚠️ Columna 'product' no homologada"
            st.warning(msg)
            bitacora.append(f"⛔ Columna no encontrada u omisa: '{posible}'")
            columnas_faltantes.append(posible)

    # Resumen de validación
    if columnas_faltantes:
        st.warning(f"⚠️ Columnas faltantes en base principal: {', '.join([c for c in columnas_faltantes if c])}")
    else:
        st.success("✅ Todas las columnas clave están presentes en la base principal.")

    # Homologación de 'Ramo'
    if 'Ramo' in df_base.columns and mapa_ramos:
        valores_ramo = df_base['Ramo'].dropna().unique()
        for original in valores_ramo:
            if original in mapa_ramos:
                bitacora.append(f"🔄 Ramo homologado detectado: '{original}' → '{mapa_ramos[original]}'")



