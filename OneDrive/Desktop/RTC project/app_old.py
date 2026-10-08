from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Admin Login Credentials
USERNAME = "admin"
PASSWORD = "1234"


# Login Page
@app.route("/")
def index():
    return render_template("login.html")


# Login Validation
@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    if username == USERNAME and password == PASSWORD:
        return redirect(url_for("dashboard"))
    else:
        return "<h2>Invalid Username or Password</h2>"


# Dashboard
@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM conductor")
    total_conductors = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bus")
    total_buses = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM sr")
    total_sr = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(cash_amount) FROM cash")
    total_cash = cursor.fetchone()[0]

    conn.close()

    if total_cash is None:
        total_cash = 0

    return render_template(
        "dashboard.html",
        total_conductors=total_conductors,
        total_buses=total_buses,
        total_sr=total_sr,
        total_cash=total_cash
    )
# Conductor Details
@app.route("/conductor")
def conductor():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM conductor")
    conductors = cursor.fetchall()

    conn.close()

    return render_template("conductor.html", conductors=conductors)


# Save Conductor Details
@app.route("/save_conductor", methods=["POST"])
def save_conductor():

    employee_id = request.form["employee_id"]
    name = request.form["name"]
    depot = request.form["depot"]
    bus_number = request.form["bus_number"]
    route_number = request.form["route_number"]
    shift = request.form["shift"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO conductor
    (employee_id, name, depot, bus_number, route_number, shift)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        employee_id,
        name,
        depot,
        bus_number,
        route_number,
        shift
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("conductor"))



# Cash Remittance Page
@app.route("/cash")
def cash_page():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT employee_id,
           conductor_name,
           bus_number,
           cash_amount,
           settlement_time,
           status,
           remarks
    FROM cash
    """)

    cashes = cursor.fetchall()

    conn.close()

    return render_template("cash.html", cashes=cashes)




# Save Cash Remittance
@app.route("/save_cash", methods=["POST"])
def save_cash():

    employee_id = request.form["employee_id"]
    conductor_name = request.form["conductor_name"]
    bus_number = request.form["bus_number"]
    cash_amount = request.form["cash_amount"]
    settlement_time = request.form["settlement_time"]
    status = request.form["status"]
    remarks = request.form["remarks"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO cash
    (employee_id,
     conductor_name,
     bus_number,
     cash_amount,
     settlement_time,
     status,
     remarks)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        employee_id,
        conductor_name,
        bus_number,
        cash_amount,
        settlement_time,
        status,
        remarks
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("cash_page"))



# Bus Allocation
@app.route("/bus")
def bus():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bus")
    buses = cursor.fetchall()

    conn.close()

    return render_template("bus.html", buses=buses)



# SR Entry
@app.route("/sr")
def sr():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sr")
    sr_records = cursor.fetchall()

    conn.close()

    return render_template("sr.html", sr_records=sr_records)



# Reports
@app.route("/reports")
def reports():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM conductor")
    total_conductors = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bus")
    total_buses = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM sr")
    total_sr = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(cash_amount) FROM cash")
    total_cash = cursor.fetchone()[0]

    conn.close()

    if total_cash is None:
        total_cash = 0

    return render_template(
        "reports.html",
        total_conductors=total_conductors,
        total_buses=total_buses,
        total_sr=total_sr,
        total_cash=total_cash
    )
@app.route("/save_bus", methods=["POST"])
def save_bus():

    bus_number = request.form["bus_number"]
    route_number = request.form["route_number"]
    driver_id = request.form["driver_id"]
    driver_name = request.form["driver_name"]
    conductor_id = request.form["conductor_id"]
    conductor_name = request.form["conductor_name"]
    shift = request.form["shift"]
    duty_date = request.form["duty_date"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO bus
    (bus_number, route_number, driver_id, driver_name,
     conductor_id, conductor_name, shift, duty_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        bus_number,
        route_number,
        driver_id,
        driver_name,
        conductor_id,
        conductor_name,
        shift,
        duty_date
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("bus"))
@app.route("/save_sr", methods=["POST"])
def save_sr():

    sr_number = request.form["sr_number"]
    employee_id = request.form["employee_id"]
    conductor_name = request.form["conductor_name"]
    bus_number = request.form["bus_number"]
    epos_collection = request.form["epos_collection"]
    cash_collection = request.form["cash_collection"]
    remarks = request.form["remarks"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO sr
    (sr_number, employee_id, conductor_name, bus_number,
     epos_collection, cash_collection, remarks)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        sr_number,
        employee_id,
        conductor_name,
        bus_number,
        epos_collection,
        cash_collection,
        remarks
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("sr"))
@app.route("/search_conductor")
def search_conductor():

    employee_id = request.args.get("employee_id")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM conductor WHERE employee_id=?",
        (employee_id,)
    )

    conductors = cursor.fetchall()

    conn.close()

    return render_template(
        "conductor.html",
        conductors=conductors
    )
@app.route("/edit_conductor/<employee_id>")
def edit_conductor(employee_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM conductor WHERE employee_id=?",
        (employee_id,)
    )

    conductor = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_conductor.html",
        conductor=conductor
    )
@app.route("/update_conductor", methods=["POST"])
def update_conductor():

    employee_id = request.form["employee_id"]
    name = request.form["name"]
    depot = request.form["depot"]
    bus_number = request.form["bus_number"]
    route_number = request.form["route_number"]
    shift = request.form["shift"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE conductor
        SET name=?,
            depot=?,
            bus_number=?,
            route_number=?,
            shift=?
        WHERE employee_id=?
    """, (
        name,
        depot,
        bus_number,
        route_number,
        shift,
        employee_id
    ))

    conn.commit()
    conn.close()

    return redirect("/conductor")
# Delete Bus
@app.route("/delete_bus/<int:id>")
def delete_bus(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM bus WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("bus"))
# Edit Bus
@app.route("/edit_bus/<int:id>")
def edit_bus(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM bus WHERE id=?",
        (id,)
    )

    bus = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_bus.html",
        bus=bus
    )
# Update Bus
@app.route("/update_bus", methods=["POST"])
def update_bus():

    id = request.form["id"]
    bus_number = request.form["bus_number"]
    route_number = request.form["route_number"]
    driver_id = request.form["driver_id"]
    driver_name = request.form["driver_name"]
    conductor_id = request.form["conductor_id"]
    conductor_name = request.form["conductor_name"]
    shift = request.form["shift"]
    duty_date = request.form["duty_date"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bus
        SET bus_number=?,
            route_number=?,
            driver_id=?,
            driver_name=?,
            conductor_id=?,
            conductor_name=?,
            shift=?,
            duty_date=?
        WHERE id=?
    """, (
        bus_number,
        route_number,
        driver_id,
        driver_name,
        conductor_id,
        conductor_name,
        shift,
        duty_date,
        id
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("bus"))
# Delete Conductor
@app.route("/delete_conductor/<employee_id>")
def delete_conductor(employee_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM conductor WHERE employee_id=?",
        (employee_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("conductor"))
@app.route("/search_bus")
def search_bus():

    bus_number = request.args.get("bus_number")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM bus WHERE bus_number=?",
        (bus_number,)
    )

    buses = cursor.fetchall()

    conn.close()

    return render_template(
        "bus.html",
        buses=buses
    )
# Run Application
if __name__ == "__main__":
    app.run(debug=True)