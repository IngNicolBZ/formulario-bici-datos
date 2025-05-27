import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Formulario SPAcio Sin Filtro", layout="wide")

st.title("📋 Formulario de Recolección de Datos")

# Campos comunes
st.subheader("Información general de la entidad territorial")
codigo = st.text_input("Código DANE (5 dígitos)", max_chars=5)
departamento = st.text_input("Departamento")
municipio = st.text_input("Entidad Territorial")

# Validación básica de DANE
if codigo and not codigo.isdigit():
    st.warning("El código DANE debe contener solo números.")
elif len(codigo) != 5:
    st.warning("El código DANE debe tener exactamente 5 dígitos.")

# Función para campos modulares
def modulo_numerico(nombre_modulo, descripcion, unidades):
    col1, col2 = st.columns([2, 1])
    with col1:
        valor = st.number_input(f"{nombre_modulo} - {descripcion} ({unidades})", min_value=0.0, step=1.0)
    with col2:
        anio = st.number_input(f"Año de {nombre_modulo}", min_value=2000, max_value=2100, step=1)
    return valor, anio

def modulo_si_no(nombre_modulo, opciones):
    col1, col2 = st.columns([2, 1])
    with col1:
        valor = st.selectbox(f"{nombre_modulo}", opciones)
    with col2:
        anio = st.number_input(f"Año de {nombre_modulo}", min_value=2000, max_value=2100, step=1)
    return valor, anio

st.subheader("🧮 Módulos de información")

# Diccionario con la estructura base
datos = {
    "CODIGO": codigo,
    "DEPARTAMENTO": departamento,
    "ENTIDAD TERRITORIAL": municipio
}

# Módulos numéricos con normalización por cada 100k o 1k hab
modulos_numericos = {
    "M6": ("Estacionamientos", "c/100k hab"),
    "M7": ("Km cicloinfraestructura", "c/100k hab"),
    "M8": ("Espacio peatonal (m2)", "c/100k hab"),
    "M9": ("Vías de tráfico calmado", "c/100k hab"),
    "M13": ("Estaciones", "c/1k hab"),
    "M14": ("Bicicletas", "c/1k hab"),
    "M15": ("Préstamos", "c/1k hab"),
    "G6": ("Infraestructura de cuidado (m2)", "c/100k hab")
}

for cod, (desc, unidad) in modulos_numericos.items():
    valor, anio = modulo_numerico(cod, desc, unidad)
    datos[cod] = valor
    datos[f"AÑO_{cod}"] = anio
    datos[f"{cod}_NORMALIZADO"] = ""  # Se llenará luego con tu script
    datos[f"FUENTE_{cod}"] = "cuestionario"

# Módulos tipo SI/NO
modulos_si_no = {
    "M19": ["SI", "NO"],
    "G7": ["SI", "NO"],
    "G8": ["SI", "NO", "NO INFO"],
    "G9": ["SI", "NO", "EN PROCESO"],
    "G10": ["SI", "NO"]
}

for cod, opciones in modulos_si_no.items():
    valor, anio = modulo_si_no(cod, opciones)
    datos[cod] = valor
    datos[f"AÑO_{cod}"] = anio
    datos[f"FUENTE_{cod}"] = "cuestionario"

# Botón de descarga
st.subheader("📥 Descargar archivo de reporte")
if st.button("Generar archivo Excel"):
    df = pd.DataFrame([datos])

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos')

    st.success("✅ Archivo generado correctamente. Puedes descargarlo abajo.")
    st.download_button(
        label="📄 Descargar Excel",
        data=output.getvalue(),
        file_name=f"Reporte_{codigo}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
