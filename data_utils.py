import os
import json
import pandas as pd
from openpyxl import Workbook, load_workbook

DB_FILE = "data/unified_knowledge_base.xlsx"
EVENTS_FILE = "data/events.json"

def init_folders():
    """Ensures necessary data directories exist."""
    if not os.path.exists("data"):
        os.makedirs("data")

def load_events():
    """Loads event configuration from JSON."""
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_events(events_dict):
    """Saves event configuration to JSON."""
    init_folders()
    with open(EVENTS_FILE, "w") as f:
        json.dump(events_dict, f, indent=4)

def save_feedback_entry(data):
    """Saves a feedback record to the master Excel file."""
    init_folders()
    if not os.path.exists(DB_FILE):
        wb = Workbook()
        ws = wb.active
        ws.append(list(data.keys()))
        wb.save(DB_FILE)
    
    wb = load_workbook(DB_FILE)
    ws = wb.active
    ws.append(list(data.values()))
    wb.save(DB_FILE)

def get_feedback_df():
    """Returns the feedback database as a DataFrame."""
    if os.path.exists(DB_FILE):
        return pd.read_excel(DB_FILE)
    return pd.DataFrame()
  
