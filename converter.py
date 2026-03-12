import sqlite3
import csv
import os

# --- PATHS ---
DB_PATH = r'C:\Users\rishi\PycharmProjects\Healo\hospitals.db'
CSV_PATH = r'C:\Users\rishi\PycharmProjects\Healo\hospitals_exported.csv'


def export_db_to_csv():
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: Could not find database at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Dynamically fetch all column names from the table to account for the new blood types
        cursor.execute("PRAGMA table_info(hospitals)")
        columns = [info[1] for info in cursor.fetchall()]

        # Select all data based on the current schema
        cursor.execute(f"SELECT {', '.join(columns)} FROM hospitals")
        rows = cursor.fetchall()

        if not rows:
            print("⚠️ The database is empty. No CSV was created.")
            return

        # Write to CSV
        with open(CSV_PATH, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)

            # Write the exact column names dynamically as the header row
            writer.writerow(columns)
            writer.writerows(rows)

        print(f"✅ Success! Exported {len(rows)} hospitals with {len(columns)} columns each to: {CSV_PATH}")

    except sqlite3.OperationalError as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    export_db_to_csv()