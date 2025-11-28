# data_engine.py
import os
import pandas as pd

# --- CONSTANTS & CONFIGURATION ---
DATA_DIR = "data"

FILES = {
    "wheel": "life_wheel.csv",
    "ideas": "ideas.csv",
    "projects": "projects.csv",
    "tasks": "tasks.csv",
    "habits": "habits.csv"
}

# --- INITIALIZATION ---
def initialize_files():
    """Checks if CSV files exist, creates them with headers if not."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    headers = {
        "wheel": ["aspect", "score", "updated_at"],
        "ideas": ["id", "content", "created_at", "status"],
        "projects": ["id", "name", "criteria", "deliverables", "risks", "phases", "milestones", "tags", "status", "created_at"],
        "tasks": ["id", "project_id", "name", "smart_what", "smart_how", "smart_metrics", "created_at", "deadline", "urgency", "importance", "status", "completed_at"],
        "habits": ["id", "name", "type", "related_to_id", "relation_type", "status", "created_at", "outcome_date"]
    }
    
    for key, filename in FILES.items():
        path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(path):
            df = pd.DataFrame(columns=headers[key])
            df.to_csv(path, index=False)

# --- GENERIC CRUD ---
def load_data(file_key):
    """Loads data from CSV into a Pandas DataFrame."""
    path = os.path.join(DATA_DIR, FILES[file_key])
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        initialize_files()
        return pd.read_csv(path)

def save_new_record(file_key, record_dict):
    """Appends a single dictionary record to the CSV."""
    df = load_data(file_key)
    new_row = pd.DataFrame([record_dict])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(os.path.join(DATA_DIR, FILES[file_key]), index=False)

def update_existing_record(file_key, record_id, update_dict):
    """Updates specific columns of a record by ID."""
    df = load_data(file_key)
    if 'id' in df.columns:
        for col, val in update_dict.items():
            df.loc[df['id'] == record_id, col] = val
        df.to_csv(os.path.join(DATA_DIR, FILES[file_key]), index=False)

def delete_record_hard(file_key, record_id):
    """Permanently deletes a record."""
    df = load_data(file_key)
    if 'id' in df.columns:
        df = df[df['id'] != record_id]
        df.to_csv(os.path.join(DATA_DIR, FILES[file_key]), index=False)

def overwrite_full_data(file_key, df):
    """Overwrites the entire CSV (used for Wheel of Life)."""
    df.to_csv(os.path.join(DATA_DIR, FILES[file_key]), index=False)