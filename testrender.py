# test_render.py - Script de Diagnóstico
import streamlit as st
import os

st.title("Herramienta de Diagnóstico de Render")

st.header("Verificando la variable de entorno `DATABASE_URL`...")

# Intentamos leer la variable de entorno
database_url = os.environ.get('DATABASE_URL')

if database_url:
    st.success("¡ÉXITO! La variable de entorno `DATABASE_URL` fue encontrada.")
    st.write("Valor encontrado:")
    # Mostramos solo una parte para no exponer la clave completa
    st.code(f"{database_url[:25]}...") 
else:
    st.error("FALLO: La variable de entorno `DATABASE_URL` NO fue encontrada.")
    st.warning("Esto confirma que el problema está en la configuración de la variable en el panel de 'Environment' de Render.")

st.info("Por favor, toma una captura de esta pantalla y envíala.")

