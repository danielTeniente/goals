import streamlit as st
import logic_core
import data_engine

def render():
    st.header("5. Gestión de Hábitos")
    
    with st.expander("Nuevo Hábito", expanded=True):
        # ---------------------------------------------------------
        # 1. PARTE INTERACTIVA (FUERA DEL FORM)
        # Esto debe estar fuera para que al cambiar el radio, se actualice la lista
        # ---------------------------------------------------------
        st.write("Configuración de relación")
        col_radio, col_select = st.columns(2)
        
        with col_radio:
            # Añadimos key para asegurar unicidad si es necesario
            rel_type = st.radio("Relacionar con:", ["Aspecto", "Proyecto"], horizontal=True)
            
        rel_options = []
        
        if rel_type == "Aspecto":
            w = logic_core.get_wheel_data()
            rel_options = w['aspect'].tolist() if not w.empty else ["General"]
        else: # Proyecto
            p = logic_core.get_projects()
            # Asegúrate que 'p' no esté vacío para evitar errores
            rel_options = p['name'].tolist() if not p.empty else []

        with col_select:
            selected_rel_name = st.selectbox("Selecciona opción", rel_options) if rel_options else None

        # ---------------------------------------------------------
        # 2. EL FORMULARIO (PARA GUARDAR)
        # Aquí dejamos los datos estáticos y el botón de envío
        # ---------------------------------------------------------
        with st.form("habit_form"):
            h_name = st.text_input("Nombre del Hábito")
            h_type = st.radio("Tipo de hábito", ["Bueno (Integrar)", "Malo (Eliminar)"], horizontal=True)
            
            # Botón de envío
            submitted = st.form_submit_button("Guardar Hábito")

            if submitted:
                # Lógica de ID (se ejecuta solo al guardar)
                selected_rel_id = selected_rel_name
                
                if rel_type == "Proyecto" and selected_rel_name:
                    p = logic_core.get_projects()
                    # Filtramos de forma segura
                    found_proj = p[p['name'] == selected_rel_name]
                    if not found_proj.empty:
                        selected_rel_id = found_proj['id'].iloc[0]

                if h_name:
                    logic_core.create_habit(h_name, h_type, rel_type, selected_rel_id)
                    st.success("Hábito creado correctamente")
                    st.rerun()
                else:
                    st.error("Por favor, escribe un nombre para el hábito.")

    st.divider()
    
    # --- LISTA DE HÁBITOS ACTIVOS (Igual que antes) ---
    st.subheader("Hábitos Activos")
    habits = data_engine.load_data("habits")
    # ... (resto de tu código de visualización igual)
    if not habits.empty:
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