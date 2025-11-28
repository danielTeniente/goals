# view_archive.py
import streamlit as st
import logic_core
import data_engine

def render():
    st.header("Elementos Archivados")
    
    st.subheader("1. Proyectos Archivados")
    arch_projs = logic_core.get_projects(status='archived')
    
    if not arch_projs.empty:
        for i, p in arch_projs.iterrows():
            c1, c2 = st.columns([4, 1])
            c1.write(f"📁 {p['name']}")
            if c2.button("Desarchivar", key=f"unarc_p_{p['id']}"):
                logic_core.unarchive_item("projects", p['id'])
                st.rerun()
    else:
        st.caption("No hay proyectos archivados.")
        
    st.divider()
    
    st.subheader("2. Tareas Archivadas")
    active_projs = logic_core.get_projects(status='active')
    
    if not active_projs.empty:
        selected_p = st.selectbox("Selecciona Proyecto:", active_projs['name'])
        p_id = active_projs[active_projs['name'] == selected_p]['id'].iloc[0]
        
        all_tasks = data_engine.load_data("tasks")
        arch_tasks = all_tasks[(all_tasks['project_id'] == p_id) & (all_tasks['status'] == 'archived')]
        
        if not arch_tasks.empty:
            for i, t in arch_tasks.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"Task: {t['name']}")
                if c2.button("Recuperar", key=f"unarc_t_{t['id']}"):
                    logic_core.unarchive_item("tasks", t['id'])
                    st.rerun()
        else:
            st.info("No hay tareas archivadas en este proyecto.")