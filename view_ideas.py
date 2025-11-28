# view_ideas.py
import streamlit as st
import logic_core
import data_engine # Para leer datos directos en tabla si es necesario

def render():
    st.header("2. Captura de Ideas")
    
    # Formulario
    with st.expander("Nueva Idea", expanded=True):
        with st.form("idea_form"):
            content = st.text_area("¿Qué tienes en mente?")
            if st.form_submit_button("Guardar Idea"):
                logic_core.create_idea(content)
                st.success("Idea guardada")
                st.rerun()
    
    # Listado
    st.subheader("Tus Ideas")
    ideas_df = data_engine.load_data("ideas")
    active_ideas = ideas_df[ideas_df['status'] == 'active']
    
    for index, row in active_ideas.iterrows():
        col_a, col_b, col_c = st.columns([6, 1, 1])
        with col_a:
            new_val = st.text_input(f"Idea {index}", value=row['content'], key=f"txt_{row['id']}")
            if new_val != row['content']:
                logic_core.update_idea_content(row['id'], new_val)
                st.rerun()
        with col_b:
            if st.button("Archivar", key=f"arc_{row['id']}"):
                logic_core.archive_item("ideas", row['id'])
                st.rerun()
        with col_c:
            if st.button("X", key=f"del_{row['id']}"):
                logic_core.delete_item("ideas", row['id'])
                st.rerun()