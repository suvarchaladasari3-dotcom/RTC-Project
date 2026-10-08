import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# =========================
# Conductor Table
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS conductor(
    employee_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    depot TEXT NOT NULL,
    bus_number TEXT NOT NULL,
    route_number TEXT NOT NULL,
    shift TEXT NOT NULL
)
""")

# =========================
# Activity Table
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS activity(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity TEXT NOT NULL,
    activity_time TEXT NOT NULL
)
""")

# =========================
# Cash Remittance Table
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS cash(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT NOT NULL,
    conductor_name TEXT NOT NULL,
    bus_number TEXT NOT NULL,
    cash_amount REAL NOT NULL,
    settlement_time TEXT NOT NULL,
    status TEXT NOT NULL,
    remarks TEXT
)
""")

# =========================
# Bus Allocation Table
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS bus(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bus_number TEXT NOT NULL,
    route_number TEXT NOT NULL,
    driver_id TEXT NOT NULL,
    driver_name TEXT NOT NULL,
    conductor_id TEXT NOT NULL,
    conductor_name TEXT NOT NULL,
    shift TEXT NOT NULL,
    duty_date TEXT NOT NULL
)
""")

# =========================
# SR Entry Table
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS sr(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sr_number TEXT NOT NULL,
    employee_id TEXT NOT NULL,
    conductor_name TEXT NOT NULL,
    bus_number TEXT NOT NULL,
    epos_collection REAL NOT NULL,
    cash_collection REAL NOT NULL,
    remarks TEXT
)
""")

conn.commit()
conn.close()

print("✅ Database Created Successfully!")