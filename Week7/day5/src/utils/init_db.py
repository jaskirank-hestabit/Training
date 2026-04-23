import sqlite3
import os

DB_PATH = "src/data/raw/sample.db"


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # DELETE OLD DATABASE COMPLETELY
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️ Old database deleted")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE factory_employees (
        emp_id        INTEGER PRIMARY KEY,
        name          TEXT NOT NULL,
        department    TEXT,
        role          TEXT,
        salary        INTEGER,
        join_year     INTEGER,
        shift         TEXT,
        line_name     TEXT,
        product       TEXT
    )
    """)

    cur.executemany(
        "INSERT INTO factory_employees VALUES (?,?,?,?,?,?,?,?,?)",
        [
            (101, "Ananya Reddy", "Assembly", "Line Operator", 32000, 2019, "Morning", "Line-A", "Engine Parts"),
            (102, "Rohit Verma", "Assembly", "Line Operator", 31000, 2020, "Night", "Line-A", "Engine Parts"),
            (103, "Deepika Joshi", "Quality Control", "QC Inspector", 38000, 2018, "Morning", "Line-B", "Gear Assembly"),
            (104, "Suresh Pillai", "Quality Control", "QC Inspector", 37500, 2021, "Morning", "Line-C", "Brake Pads"),
            (105, "Kavitha Menon", "Maintenance", "Maintenance Tech", 41000, 2017, "Night", "Line-D", "Exhaust Units"),
            (106, "Nikhil Gupta", "Maintenance", "Maintenance Tech", 40000, 2019, "Morning", "Line-B", "Gear Assembly"),
            (107, "Pooja Iyer", "Packaging", "Packing Operator", 29000, 2022, "Morning", "Line-C", "Brake Pads"),
            (108, "Arjun Das", "Packaging", "Packing Operator", 29500, 2021, "Night", "Line-D", "Exhaust Units"),
            (109, "Meena Krishnan", "Logistics", "Logistics Coord", 35000, 2020, "Morning", "Line-A", "Engine Parts"),
            (110, "Farhan Sheikh", "Assembly", "Senior Operator", 45000, 2015, "Morning", "Line-B", "Gear Assembly"),
            (111, "Lata Bhatt", "Quality Control", "Senior QC", 50000, 2014, "Night", "Line-D", "Exhaust Units"),
            (112, "Ramesh Tiwari", "Logistics", "Warehouse Lead", 43000, 2016, "Night", "Line-C", "Brake Pads")
        ]
    )

    conn.commit()
    conn.close()

    print(f"Fresh database created at {DB_PATH}")
    print("Table: factory_employees")

if __name__ == "__main__":
    init_db()