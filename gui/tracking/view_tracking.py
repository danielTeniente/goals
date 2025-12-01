# view_tracking.py
import streamlit as st
import plotly.express as px
import logic_core
from datetime import datetime

def render():
    st.header("📊 Seguimiento y Situación Actual")
    
    # --- SECCIÓN 1: RUEDA DE LA VIDA (SOLO VISUALIZACIÓN) ---
    st.subheader("1. Tu Equilibrio (Rueda de la Vida)")
    
    current_data = logic_core.get_wheel_data()
    
    if not current_data.empty:
        # Creamos una copia para graficar sin alterar datos
        df_chart = current_data.copy()
        
        # Configuración del gráfico
        fig = px.line_polar(
            df_chart, 
            r='score', 
            theta='aspect', 
            line_close=True, 
            range_r=[0, 10], 
            title=""
        )
        fig.update_traces(fill='toself')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos suficientes en la Rueda de la Vida. Ve a 'Creación' para configurarla.")

    st.divider()

    # --- SECCIÓN 2: PROYECTOS Y TAREAS DE LA SEMANA ---
    st.subheader("2. Foco Semanal (Proyectos y Tareas)")
    st.markdown("A continuación se muestran los **proyectos activos** y sus tareas programadas para **esta semana**.")

    projects = logic_core.get_projects()
    
    if projects.empty:
        st.warning("No tienes proyectos creados.")
        return

    # Obtener fecha actual para cálculos de semana
    today = datetime.now().date()
    current_week_number = today.isocalendar()[1]
    current_year = today.year

    # Contador para saber si mostramos algo o no
    tasks_found_total = 0

    for idx, p in projects.iterrows():
        # Obtenemos las tareas de este proyecto
        tasks = logic_core.get_tasks_by_project(p['id'])
        
        # Filtramos tareas: 
        # 1. Que NO estén completadas (status != 'completed')
        # 2. Que la fecha corresponda a la semana actual
        
        week_tasks = []
        if not tasks.empty:
            for i, t in tasks.iterrows():
                if t['status'] == 'completed':
                    continue
                
                try:
                    t_date = datetime.strptime(t['deadline'], "%Y-%m-%d").date()
                    # Verificar si coincide año y número de semana
                    if t_date.isocalendar()[1] == current_week_number and t_date.year == current_year:
                        week_tasks.append(t)
                except ValueError:
                    continue # Si la fecha es inválida, saltamos

        # Si el proyecto tiene tareas para esta semana, lo mostramos
        if week_tasks:
            tasks_found_total += 1
            with st.container():
                st.markdown(f"### 📂 {p['name']}")
                # Detalles del proyecto opcionales (Criteria, etiquetas)
                if p['tags']:
                    st.caption(f"Etiquetas: {p['tags']}")
                
                # Listar las tareas
                for t in week_tasks:
                    # Formato visual de la tarea
                    col_t1, col_t2 = st.columns([4, 1])
                    with col_t1:
                        st.write(f"⬜ **{t['name']}**")
                        st.caption(f"📅 {t['deadline']} | Estrategia: {t.get('smart_how', 'N/A')}")
                    with col_t2:
                        # Badge visual para urgencia
                        if int(t['urgency']) >= 8:
                            st.error(f"Urgencia: {t['urgency']}")
                        elif int(t['urgency']) >= 5:
                            st.warning(f"Urgencia: {t['urgency']}")
                        else:
                            st.success(f"Urgencia: {t['urgency']}")
                
                st.markdown("---")
    
    if tasks_found_total == 0:
        st.info("🎉 ¡Nada pendiente para esta semana! (O no has asignado fechas para esta semana en tus tareas activas).")