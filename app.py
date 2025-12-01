# app.py
import streamlit as st

# Importamos las Vistas
import view_wheel
import view_ideas
import view_projects
import view_habits
import view_review
import view_archive
from gui.tracking  import view_tracking

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestor Integral de Vida", layout="wide")
st.markdown("""<style>.stHeader { font-size: 2rem; } .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 5px; }</style>""", unsafe_allow_html=True)

# --- NAVEGACIÓN ---
# Se agregó "Seguimiento" al menú
menu_principal = st.sidebar.radio("Navegación Principal", ["Seguimiento", "Creación", "Revisión", "Archivados"])

if menu_principal == "Seguimiento":
    view_tracking.render()

elif menu_principal == "Creación":
    sub_menu = st.sidebar.selectbox("Módulo de Creación", 
        ["Rueda de la Vida", "Ideas", "Proyectos", "Tareas", "Hábitos"])

    if sub_menu == "Rueda de la Vida":
        view_wheel.render()
    elif sub_menu == "Ideas":
        view_ideas.render()
    elif sub_menu == "Proyectos":
        view_projects.render_projects()
    elif sub_menu == "Tareas":
        view_projects.render_tasks()
    elif sub_menu == "Hábitos":
        view_habits.render()

elif menu_principal == "Revisión":
    view_review.render()

elif menu_principal == "Archivados":
    view_archive.render()