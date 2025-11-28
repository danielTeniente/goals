# view_wheel.py
import streamlit as st
import plotly.express as px
import logic_core

def render():
    st.header("1. Rueda de la Vida")
    col1, col2 = st.columns([1, 2])
    
    current_data = logic_core.get_wheel_data()
    default_aspects = ["Salud", "Finanzas", "Desarrollo Personal", "Carrera", 
                       "Amigos", "Familia", "Amor", "Diversión"]
    
    scores = {}
    
    with col1:
        st.subheader("Puntúa tus aspectos")
        with st.form("wheel_form"):
            for aspect in default_aspects:
                prev_val = 5
                if not current_data.empty:
                    row = current_data[current_data['aspect'] == aspect]
                    if not row.empty:
                        prev_val = int(row.iloc[0]['score'])
                        
                scores[aspect] = st.slider(aspect, 1, 10, prev_val)
            
            if st.form_submit_button("Guardar Rueda"):
                logic_core.save_wheel_scores(scores)
                st.success("Rueda actualizada")
                st.rerun()

    with col2:
        st.subheader("Visualización")
        if not current_data.empty:
            df_chart = current_data.copy()
            fig = px.line_polar(df_chart, r='score', theta='aspect', line_close=True, 
                                range_r=[0, 10], title="Tu Equilibrio Actual")
            fig.update_traces(fill='toself')
            st.plotly_chart(fig)