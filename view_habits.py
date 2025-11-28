# view_habits.py
import streamlit as st
import logic_core
import data_engine

def render():
    st.header("5. Gestión de Hábitos")
    
    with st.expander("Nuevo Hábito"):
        with st.form("habit_form"):
            h_name = st.text_input("Hábito")
            h_type = st.radio("Tipo", ["Bueno (Integrar)", "Malo (Eliminar)"])
            
            rel_type = st.radio("Relacionar con:", ["Aspecto", "Proyecto"])
            rel_options = []
            
            if rel_type == "Aspecto":
                w = logic_core.get_wheel_data()
                rel_options = w['aspect'].tolist() if not w.empty else ["General"]
                
            else: # Proyecto
                p = logic_core.get_projects()
                rel_options = p['name'].tolist()
            
            selected_rel_name = st.selectbox("Selecciona relación", rel_options) if rel_options else None
            
            # Resolver ID
            selected_rel_id = selected_rel_name
            if rel_type == "Proyecto" and selected_rel_name:
                p = logic_core.get_projects()
                selected_rel_id = p[p['name'] == selected_rel_name]['id'].iloc[0]

            if st.form_submit_button("Guardar Hábito"):
                logic_core.create_habit(h_name, h_type, rel_type, selected_rel_id)
                st.success("Hábito creado")
                st.rerun()

    st.subheader("Hábitos Activos")
    habits = data_engine.load_data("habits")
    active_habits = habits[habits['status'] == 'active']
    
    for i, h in active_habits.iterrows():
        col1, col2, col3 = st.columns([4, 2, 2])
        col1.write(f"**{h['name']}** ({'A integrar' if h['type']=='good' else 'A eliminar'})")
        col1.caption(f"Relacionado con: {h['relation_type']}")
        
        if h['type'] == 'good':
            if col2.button("¡Integrado!", key=f"int_{h['id']}"):
                logic_core.resolve_habit(h['id'], "integrated")
                st.rerun()
        else:
             if col2.button("¡Eliminado!", key=f"elim_{h['id']}"):
                logic_core.resolve_habit(h['id'], "eliminated_success")
                st.rerun()
        
        if col3.button("Borrar", key=f"del_h_{h['id']}"):
            logic_core.delete_item("habits", h['id'])
            st.rerun()