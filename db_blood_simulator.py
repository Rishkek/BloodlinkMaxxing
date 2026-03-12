"""
eRoktosh DB & JSON Blood Inventory Simulator
Updates hospitals.db AND exports a live blood_inventory.json for the frontend.
"""

import sqlite3
import json
import time
import os
from datetime import datetime
import random

# --- CONFIGURATION PATHS ---
DB_PATH = r'C:\Users\rishi\PycharmProjects\Healo\hospitals.db'

# Define the path to your frontend folder here
FRONTEND_DIR = r'C:\Users\rishi\PycharmProjects\health-frontend'
JSON_PATH = os.path.join(FRONTEND_DIR, 'blood_inventory.json')

# Database columns and their corresponding frontend display names
DB_COLS = ['O_pos', 'O_neg', 'A_pos', 'A_neg', 'B_pos', 'B_neg', 'AB_pos', 'AB_neg']
FRONTEND_TYPES = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']

# Availability levels
AVAILABILITY_LEVELS = {
    "Critical": {"max": 2, "emoji": "🔴"},
    "Low": {"max": 10, "emoji": "🟠"},
    "Available": {"max": 30, "emoji": "🟡"},
    "Good": {"max": 50, "emoji": "🟢"},
    "Excellent": {"max": float('inf'), "emoji": "🟢🟢"}
}

def get_availability_status(units):
    if units <= 2: return "Critical"
    elif units <= 10: return "Low"
    elif units <= 30: return "Available"
    elif units <= 50: return "Good"
    else: return "Excellent"

def initialize_empty_inventory():
    """Gives starting blood units to any new hospitals in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM hospitals WHERE Total_Units = 0 OR Total_Units IS NULL")
    empty_hospitals = cursor.fetchall()

    if empty_hospitals:
        for row in empty_hospitals:
            h_id = row[0]
            units_dict = []
            total = 0
            for col in DB_COLS:
                if col.startswith('AB'): units = random.randint(2, 25)
                elif col == 'O_neg': units = random.randint(5, 30)
                else: units = random.randint(3, 40)
                units_dict.append(units)
                total += units

            cursor.execute(f"""
                UPDATE hospitals 
                SET O_pos=?, O_neg=?, A_pos=?, A_neg=?, B_pos=?, B_neg=?, AB_pos=?, AB_neg=?, Total_Units=?
                WHERE id=?
            """, (*units_dict, total, h_id))
        conn.commit()
    conn.close()

def update_db_and_export_json():
    """Fluctuates the DB values and writes the formatted JSON to the frontend folder."""
    # Ensure the frontend directory exists
    os.makedirs(FRONTEND_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Fetch and Update Database
    cursor.execute(f"SELECT id, name, {', '.join(DB_COLS)} FROM hospitals")
    hospitals = cursor.fetchall()

    frontend_data = {
        "system": "eRoktosh Blood Inventory Management",
        "generated_at": datetime.now().isoformat(),
        "total_hospitals": len(hospitals),
        "blood_groups": FRONTEND_TYPES,
        "hospitals": {}
    }

    for row in hospitals:
        h_id = row[0]
        h_name = row[1]
        current_units = list(row[2:])

        hospital_json = {
            "hospital_id": h_id,
            "name": h_name,
            "timestamp": datetime.now().isoformat(),
            "blood_groups": {}
        }

        new_total = 0
        for i in range(len(current_units)):
            val = current_units[i]

            # Fluctuation Logic (40% usage, 40% donation, 20% no change)
            rand = random.random()
            if rand < 0.40: change = random.randint(-4, -1)
            elif rand < 0.80: change = random.randint(1, 5)
            else: change = 0

            new_val = max(0, val + change)
            current_units[i] = new_val
            new_total += new_val

            # Format for JSON
            frontend_type = FRONTEND_TYPES[i]
            status = get_availability_status(new_val)

            hospital_json["blood_groups"][frontend_type] = {
                "units": new_val,
                "status": status,
                "emoji": AVAILABILITY_LEVELS[status]["emoji"],
                "last_updated": datetime.now().isoformat(),
                "expiry_rate": random.randint(1, 5) # Mocking expiry for frontend
            }

        # Update SQLite DB
        cursor.execute(f"""
            UPDATE hospitals 
            SET O_pos=?, O_neg=?, A_pos=?, A_neg=?, B_pos=?, B_neg=?, AB_pos=?, AB_neg=?, Total_Units=?
            WHERE id=?
        """, (*current_units, new_total, h_id))

        # Add to JSON Dictionary
        frontend_data["hospitals"][str(h_id)] = hospital_json

    conn.commit()
    conn.close()

    # 2. Export to JSON file in frontend folder
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(frontend_data, f, indent=2, ensure_ascii=False)

    return frontend_data

def run_simulator(interval=30):
    print("🩸 eRoktosh Live DB & JSON Simulator Started")
    print(f"Exporting JSON to: {JSON_PATH}")
    print(f"Updating every {interval} seconds. Press Ctrl+C to stop.\n")

    initialize_empty_inventory()

    update_count = 0
    try:
        while True:
            frontend_data = update_db_and_export_json()
            update_count += 1

            # Count critical alerts for the terminal printout
            critical_count = sum(
                1 for h in frontend_data["hospitals"].values()
                for b in h["blood_groups"].values() if b["status"] == "Critical"
            )

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Update #{update_count} - DB Updated & JSON Exported | Critical Types: {critical_count}")
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\n✅ Simulator stopped.")

if __name__ == "__main__":
    run_simulator(interval=30)