# logic_core.py
import uuid
import pandas as pd
from datetime import datetime, timedelta
import data_engine

# Inicializar DB al importar
data_engine.initialize_files()

# --- HELPERS ---
def generate_id():
    return str(uuid.uuid4())

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

# --- WHEEL LOGIC ---
def get_wheel_data():
    return data_engine.load_data("wheel")

def save_wheel_scores(scores_dict):
    current_time = datetime.now().isoformat()
    df = pd.DataFrame(list(scores_dict.items()), columns=["aspect", "score"])
    df["updated_at"] = current_time
    data_engine.overwrite_full_data("wheel", df)

# --- IDEAS LOGIC ---
def create_idea(content):
    record = {
        "id": generate_id(),
        "content": content,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "active"
    }
    data_engine.save_new_record("ideas", record)

def update_idea_content(idea_id, new_content):
    data_engine.update_existing_record("ideas", idea_id, {"content": new_content})

def get_all_ideas_text():
    """Retrieves concatenated text from all active ideas for visualization."""
    df = data_engine.load_data("ideas")
    if df.empty:
        return ""
    active_ideas = df[df['status'] == 'active']
    if active_ideas.empty:
        return ""
    # Join all content into a single string
    return " ".join(active_ideas['content'].dropna().astype(str).tolist())

# --- PROJECTS LOGIC ---
def create_project(name, criteria, deliverables, risks, phases, tags_list):
    record = {
        "id": generate_id(),
        "name": name,
        "criteria": criteria,
        "deliverables": deliverables,
        "risks": risks,
        "phases": phases,
        "milestones": "",
        "tags": ",".join(tags_list),
        "status": "active",
        "created_at": get_current_date()
    }
    data_engine.save_new_record("projects", record)

def get_projects(status='active'):
    df = data_engine.load_data("projects")
    return df[df['status'] == status]

# --- TASKS LOGIC ---
def create_task(project_id, what, how, metrics, deadline, urgency, importance):
    record = {
        "id": generate_id(),
        "project_id": project_id,
        "name": what,
        "smart_what": what,
        "smart_how": how,
        "smart_metrics": metrics,
        "created_at": get_current_date(),
        "deadline": str(deadline),
        "urgency": urgency,
        "importance": importance,
        "status": "active",
        "completed_at": ""
    }
    data_engine.save_new_record("tasks", record)

def complete_task(task_id):
    data_engine.update_existing_record("tasks", task_id, {
        "status": "completed",
        "completed_at": get_current_date()
    })

def get_tasks_by_project(project_id, active_only=True):
    df = data_engine.load_data("tasks")
    mask = (df['project_id'] == project_id)
    if active_only:
        mask = mask & (df['status'] != 'archived')
    return df[mask]

def update_task(task_id, what, how, metrics, deadline, urgency, importance):
    """Actualiza los datos de una tarea existente."""
    updates = {
        "name": what,
        "smart_what": what,
        "smart_how": how,
        "smart_metrics": metrics,
        "deadline": str(deadline),
        "urgency": urgency,
        "importance": importance
    }
    data_engine.update_existing_record("tasks", task_id, updates)

# --- HABITS LOGIC ---
def create_habit(name, habit_type_str, relation_type, related_id):
    t_val = "good" if "Bueno" in habit_type_str else "bad"
    record = {
        "id": generate_id(),
        "name": name,
        "type": t_val,
        "related_to_id": related_id,
        "relation_type": relation_type,
        "status": "active",
        "created_at": get_current_date(),
        "outcome_date": ""
    }
    data_engine.save_new_record("habits", record)

def resolve_habit(habit_id, resolution_type):
    # resolution_type: 'integrated' or 'eliminated_success'
    data_engine.update_existing_record("habits", habit_id, {
        "status": resolution_type,
        "outcome_date": get_current_date()
    })

# --- GENERIC STATE ACTIONS ---
def archive_item(file_key, item_id):
    data_engine.update_existing_record(file_key, item_id, {"status": "archived"})

def unarchive_item(file_key, item_id):
    data_engine.update_existing_record(file_key, item_id, {"status": "active"})

def delete_item(file_key, item_id):
    data_engine.delete_record_hard(file_key, item_id)

# --- ANALYTICS & STATS ---
def get_upcoming_tasks_next_week():
    df = data_engine.load_data("tasks")
    df = df[df['status'] == 'active']
    now = datetime.now()
    next_week = now + timedelta(days=7)
    df['deadline'] = pd.to_datetime(df['deadline'], errors='coerce')
    mask = (df['deadline'] >= now) & (df['deadline'] <= next_week)
    return df[mask].sort_values(by='urgency', ascending=False)

def calculate_project_stats():
    tasks = data_engine.load_data("tasks")
    projects = data_engine.load_data("projects")
    stats = []
    
    for pid in projects['id'].unique():
        p_tasks = tasks[tasks['project_id'] == pid]
        if p_tasks.empty: continue
            
        total = len(p_tasks)
        completed = len(p_tasks[p_tasks['status'] == 'completed'])
        
        # Get project name safely
        p_row = projects[projects['id'] == pid]
        p_name = p_row['name'].iloc[0] if not p_row.empty else "Unknown"

        # Time calc
        completed_tasks = p_tasks[p_tasks['status'] == 'completed'].copy()
        avg_days = 0
        if not completed_tasks.empty:
            completed_tasks['start'] = pd.to_datetime(completed_tasks['created_at'])
            completed_tasks['end'] = pd.to_datetime(completed_tasks['completed_at'])
            durations = (completed_tasks['end'] - completed_tasks['start']).dt.days
            avg_days = durations.mean()

        stats.append({
            "project": p_name,
            "total": total,
            "completed": completed,
            "avg_days_to_complete": round(avg_days, 1)
        })
    return pd.DataFrame(stats)

def get_habit_stats_summary():
    habits = data_engine.load_data("habits")
    projects = data_engine.load_data("projects")
    
    summary = []
    for _, habit in habits.iterrows():
        # Determine Category Name
        category = "General"
        if habit['relation_type'] == 'Aspecto':
            category = habit['related_to_id']
        elif habit['relation_type'] == 'Proyecto':
            p_row = projects[projects['id'] == habit['related_to_id']]
            if not p_row.empty:
                category = p_row['name'].iloc[0]
            else:
                category = "Proyecto Eliminado"

        # Determine State Label
        state_label = "Desconocido"
        if habit['status'] == 'active':
            state_label = "En Desarrollo" if habit['type'] == 'good' else "Por Eliminar"
        elif habit['status'] == 'integrated':
            state_label = "Integrado"
        elif habit['status'] == 'eliminated_success':
            state_label = "Eliminado"
            
        summary.append({
            "category": category,
            "state": state_label,
            "count": 1
        })
    return pd.DataFrame(summary)