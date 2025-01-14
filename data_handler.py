import json
import os

DATA_FILE = "data.json"
VISIT_DATA_FILE = "visit_records.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

def save_data(records):
    with open(DATA_FILE, "w") as file:
        json.dump(records, file, indent=4)

def load_visit_records(oib):
    if not os.path.exists(VISIT_DATA_FILE):
        return []
    with open(VISIT_DATA_FILE, "r") as file:
        try:
            all_visits = json.load(file)
            return [visit for visit in all_visits if visit["OIB"] == oib]
        except json.JSONDecodeError:
            return []

def save_visit_record(new_visit):
    visits = []
    if os.path.exists(VISIT_DATA_FILE):
        with open(VISIT_DATA_FILE, "r") as file:
            try:
                visits = json.load(file)
            except json.JSONDecodeError:
                visits = []
    visits.append(new_visit)
    with open(VISIT_DATA_FILE, "w") as file:
        json.dump(visits, file, indent=4)
