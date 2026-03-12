import sqlite3
import random
import time
import math

DB_PATH = 'hospitals.db'

# Approximate Indian blood type prevalence for realistic distribution
BLOOD_PREVALENCE = {
    'O_pos': 0.32, 'O_neg': 0.02,
    'A_pos': 0.22, 'A_neg': 0.01,
    'B_pos': 0.32, 'B_neg': 0.02,
    'AB_pos': 0.08, 'AB_neg': 0.01
}


def setup_database():
    """Adds the necessary blood type columns to the existing database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check existing columns
    cursor.execute("PRAGMA table_info(hospitals)")
    columns = [info[1] for info in cursor.fetchall()]

    new_columns = ['O_pos', 'O_neg', 'A_pos', 'A_neg', 'B_pos', 'B_neg', 'AB_pos', 'AB_neg', 'Total_Units']

    for col in new_columns:
        if col not in columns:
            cursor.execute(f"ALTER TABLE hospitals ADD COLUMN {col} INTEGER DEFAULT 0")
            print(f"Added column: {col}")

    conn.commit()
    conn.close()


def get_review_count(hospital_name, location):
    """
    TODO: Replace this mock function with Google Places API or your scraper.
    API Example:
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={hospital_name}&inputtype=textquery&fields=user_ratings_total&key=YOUR_API_KEY"
    """
    # Mocking a review count between 50 and 5000 for demonstration
    return random.randint(50, 5000)


def predict_initial_inventory(reviews):
    """Predicts blood units based on hospital popularity (reviews)."""
    # A logarithmic curve ensures massive hospitals don't get absurdly high numbers
    # while small clinics still get a baseline.
    base_capacity = int(math.log(reviews + 1) * 50)

    inventory = {}
    total = 0
    for blood_type, prevalence in BLOOD_PREVALENCE.items():
        # Add some randomness to the exact distribution
        variance = random.uniform(0.8, 1.2)
        units = int(base_capacity * prevalence * variance)
        inventory[blood_type] = units
        total += units

    inventory['Total_Units'] = total
    return inventory


def initialize_inventory():
    """Fetches review counts and populates the initial inventory."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, location FROM hospitals")
    hospitals = cursor.fetchall()

    print(f"Initializing inventory for {len(hospitals)} hospitals...")

    for h_id, name, location in hospitals:
        reviews = get_review_count(name, location)
        inventory = predict_initial_inventory(reviews)

        cursor.execute(f"""
            UPDATE hospitals 
            SET O_pos = ?, O_neg = ?, A_pos = ?, A_neg = ?, B_pos = ?, B_neg = ?, AB_pos = ?, AB_neg = ?, Total_Units = ?
            WHERE id = ?
        """, (
            inventory['O_pos'], inventory['O_neg'], inventory['A_pos'], inventory['A_neg'],
            inventory['B_pos'], inventory['B_neg'], inventory['AB_pos'], inventory['AB_neg'],
            inventory['Total_Units'], h_id
        ))

    conn.commit()
    conn.close()
    print("Initial inventory populated successfully.")


def simulate_live_inventory(interval_seconds=3600):
    """Continuously fluctuates blood units to simulate real-world usage and donations."""
    print(f"Starting live simulation. Updating every {interval_seconds} seconds. Press Ctrl+C to stop.")

    blood_types = ['O_pos', 'O_neg', 'A_pos', 'A_neg', 'B_pos', 'B_neg', 'AB_pos', 'AB_neg']

    while True:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id, O_pos, O_neg, A_pos, A_neg, B_pos, B_neg, AB_pos, AB_neg FROM hospitals")
        hospitals = cursor.fetchall()

        for row in hospitals:
            h_id = row[0]
            current_units = list(row[1:])

            new_total = 0
            for i in range(len(current_units)):
                # Simulate a change: between -3 (units used) and +2 (units donated)
                # Negative types are rarer, so they fluctuate less
                is_negative = blood_types[i].endswith('neg')
                change_range = (-1, 1) if is_negative else (-3, 2)

                change = random.randint(*change_range)

                # Ensure units don't drop below zero
                current_units[i] = max(0, current_units[i] + change)
                new_total += current_units[i]

            # Update the database
            query = f"""
                UPDATE hospitals 
                SET O_pos = ?, O_neg = ?, A_pos = ?, A_neg = ?, B_pos = ?, B_neg = ?, AB_pos = ?, AB_neg = ?, Total_Units = ?
                WHERE id = ?
            """
            cursor.execute(query, (*current_units, new_total, h_id))

        conn.commit()
        conn.close()

        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Inventory updated for all hospitals.")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    setup_database()
    # Comment this out after the first run so it doesn't overwrite your live simulation
    initialize_inventory()

    # Run the continuous updater (set to update every 60 seconds for testing)
    simulate_live_inventory(interval_seconds=60)