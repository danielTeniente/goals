# view_review.py
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import logic_core
import data_engine

# Stopwords en español básicas para no depender de librerías externas pesadas como NLTK
STOPWORDS_ES = {
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un", "para", "con", "no", "una", "su", "al", "lo", "como",
    "más", "pero", "sus", "le", "ya", "o", "este", "sí", "porque", "esta", "entre", "cuando", "muy", "sin", "sobre", "también", "me", "hasta",
    "hay", "donde", "quien", "desde", "todo", "nos", "durante", "todos", "uno", "les", "ni", "contra", "otros", "ese", "eso", "ante", "ellos",
    "e", "esto", "mí", "antes", "algunos", "qué", "unos", "yo", "otro", "otras", "otra", "él", "tanto", "esa", "estos", "mucho", "quienes",
    "nada", "muchos", "cual", "poco", "ella", "estar", "estas", "algunas", "algo", "nosotros", "mi", "mis", "tú", "te", "ti", "tu", "tus",
    "ellas", "nosotras", "vosotros", "vosotras", "os", "mío", "mía", "míos", "mías", "tuyo", "tuya", "tuyos", "tuyas", "suyo", "suya", "suyos",
    "suyas", "nuestro", "nuestra", "nuestros", "nuestras", "vuestro", "vuestra", "vuestros", "vuestras", "es", "son", "fue", "era", "ser", "soy"
}

def render():
    st.header("Panel de Revisión")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Proyectos y Prioridades", "Estadísticas Proyectos", "Hábitos", "Nube de Ideas"])
    
    # --- Tab 1: Matriz ---
    with tab1:
        st.subheader("Matriz de Importancia / Urgencia")
        tasks_df = data_engine.load_data("tasks")
        active_tasks = tasks_df[tasks_df['status'] == 'active']
        projects_df = data_engine.load_data("projects")
        
        if not active_tasks.empty and not projects_df.empty:
            merged = active_tasks.merge(projects_df[['id', 'name']], left_on='project_id', right_on='id', suffixes=('', '_proj'))
            fig = px.scatter(merged, x="urgency", y="importance", color="name_proj",
                             hover_data=['name', 'deadline'], size_max=60,
                             title="Matriz Eisenhower")
            fig.add_vline(x=5.5, line_width=1, line_dash="dash", line_color="grey")
            fig.add_hline(y=5.5, line_width=1, line_dash="dash", line_color="grey")
            fig.update_layout(xaxis_title="Urgencia", yaxis_title="Importancia", xaxis_range=[0,11], yaxis_range=[0,11])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos para la matriz.")

        st.subheader("⚠️ Próxima Semana")
        upcoming = logic_core.get_upcoming_tasks_next_week()
        if not upcoming.empty:
            st.dataframe(upcoming[['name', 'deadline', 'urgency', 'importance']], use_container_width=True)
        else:
            st.success("¡Nada urgente!")

    # --- Tab 2: Stats Proyectos ---
    with tab2:
        st.subheader("Rendimiento por Proyecto")
        stats = logic_core.calculate_project_stats()
        if not stats.empty:
            c1, c2 = st.columns(2)
            with c1:
                fig = px.line_polar(stats, r='completed', theta='project', line_close=True, title="Tareas Completadas")
                fig.update_traces(fill='toself')
                st.plotly_chart(fig)
            with c2:
                st.dataframe(stats, hide_index=True)
        else:
            st.info("Sin estadísticas.")

    # --- Tab 3: Stats Hábitos ---
    with tab3:
        st.subheader("Evolución de Hábitos")
        summary = logic_core.get_habit_stats_summary()
        if not summary.empty:
            grouped = summary.groupby(['category', 'state']).count().reset_index()
            fig = px.bar_polar(grouped, r="count", theta="category", color="state",
                               title="Estado de Hábitos", template="plotly_white",
                               color_discrete_map={
                                   "Integrado": "#00CC96", "Eliminado": "#EF553B",
                                   "En Desarrollo": "#636EFA", "Por Eliminar": "#AB63FA"
                               })
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos de hábitos.")

    # --- Tab 4: Nube de Ideas ---
    with tab4:
        st.subheader("Visualización de Ideas")
        text = logic_core.get_all_ideas_text()
        
        if text and len(text.strip()) > 0:
            try:
                # Generar WordCloud
                wordcloud = WordCloud(
                    width=800, 
                    height=400, 
                    background_color='white',
                    stopwords=STOPWORDS_ES,
                    min_font_size=10
                ).generate(text)
                
                # Plot
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error generando la visualización: {e}")
        else:
            st.info("No hay suficientes ideas registradas para generar la nube de palabras.")