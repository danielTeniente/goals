# view_projects.py
import streamlit as st
import logic_core
from datetime import datetime

def render_projects():
    st.header("3. Gestión de Proyectos")
    
    with st.expander("Crear Nuevo Proyecto"):
        with st.form("project_form"):
            name = st.text_input("Nombre del Proyecto")
            criteria = st.text_area("Criterios de Éxito")
            deliverables = st.text_area("Entregables")
            risks = st.text_area("Riesgos")
            phases = st.text_area("Fases e Hitos")
            
            wheel_df = logic_core.get_wheel_data()
            aspects_list = wheel_df['aspect'].tolist() if not wheel_df.empty else ["General"]
            tags = st.multiselect("Relacionado con aspectos de la vida", aspects_list)
            
            if st.form_submit_button("Crear Proyecto"):
                logic_core.create_project(name, criteria, deliverables, risks, phases, tags)
                st.success("Proyecto Creado")
                st.rerun()

    st.subheader("Proyectos Activos")
    projects = logic_core.get_projects()
    for idx, p in projects.iterrows():
        with st.expander(f"📁 {p['name']} (Etiquetas: {p['tags']})"):
            st.write(f"**Éxito:** {p['criteria']}")
            st.write(f"**Entregables:** {p['deliverables']}")
            c1, c2 = st.columns(2)
            if c1.button("Archivar Proyecto", key=f"arc_p_{p['id']}"):
                logic_core.archive_item("projects", p['id'])
                st.rerun()
            if c2.button("Eliminar Definitivamente", key=f"del_p_{p['id']}"):
                logic_core.delete_item("projects", p['id'])
                st.rerun()

def render_tasks():
    st.header("4. Asignación de Tareas (SMART)")
    
    projects = logic_core.get_projects()
    if projects.empty:
        st.warning("Primero crea un proyecto.")
        return

    proj_dict = dict(zip(projects['name'], projects['id']))
    selected_proj_name = st.selectbox("Selecciona Proyecto", list(proj_dict.keys()))
    selected_proj_id = proj_dict[selected_proj_name]
    
    st.subheader("Agregar Tarea")
    with st.form("task_form"):
        c1, c2, c3 = st.columns(3)
        what = c1.text_input("¿Qué? (Nombre)")
        how = c2.text_input("¿Cómo? (Estrategia)")
        metrics = c3.text_input("¿Métrica? (Medición)")
        
        c4, c5 = st.columns(2)
        deadline = c4.date_input("Fecha Límite (When)")
        
        st.markdown("---")
        st.markdown("**Matriz Eisenhower**")
        ce1, ce2 = st.columns(2)
        urgency = ce1.slider("Urgencia (1-10)", 1, 10, 5)
        importance = ce2.slider("Importancia (1-10)", 1, 10, 5)
        
        if st.form_submit_button("Agregar Tarea"):
            logic_core.create_task(selected_proj_id, what, how, metrics, deadline, urgency, importance)
            st.success("Tarea agregada")
            st.rerun()

    st.divider()
    st.subheader(f"Tareas de: {selected_proj_name}")
    tasks = logic_core.get_tasks_by_project(selected_proj_id)
    
    if not tasks.empty:
        tasks = tasks.sort_values(by="urgency", ascending=False)
        for i, t in tasks.iterrows():
            cols = st.columns([4, 2, 2, 1, 1])
            cols[0].write(f"**{t['name']}**")
            cols[1].write(f"Límite: {t['deadline']}")
            cols[2].caption(f"Urg:{t['urgency']} / Imp:{t['importance']}")
            
            if t['status'] == 'active':
                if cols[3].button("✅", key=f"done_{t['id']}"):
                    logic_core.complete_task(t['id'])
                    st.rerun()
                if cols[4].button("📂", key=f"arc_t_{t['id']}"):
                    logic_core.archive_item("tasks", t['id'])
                    st.rerun()
            else:
                cols[3].success("Completada")