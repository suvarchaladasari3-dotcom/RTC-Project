from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

from flask import make_response

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from datetime import datetime
import io
from collections import defaultdict

app = Flask(__name__)
app.secret_key = "rtc_project_secret"
# ===== Dashboard Summary Function =====
def get_dashboard_summary():
    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM conductor")
    total_conductors = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bus")
    total_buses = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM sr")
    total_sr = cursor.fetchone()[0]

    cursor.execute("SELECT IFNULL(SUM(cash_amount),0) FROM cash")
    total_cash = cursor.fetchone()[0]

    conn.close()

    return {
        "total_conductors": total_conductors,
        "total_buses": total_buses,
        "total_sr": total_sr,
        "total_cash": total_cash
    }
# -----------------------------
# Administrator Login Credentials
# -----------------------------
USERNAME = "rtcadmin"
PASSWORD = "Rtc@123"
# -----------------------------
# Database Connection
# -----------------------------

def get_db():
    conn = sqlite3.connect(
        "database.db",
        timeout=30,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row

    # SQLite locking reduce cheyyadaniki
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")

    return conn

def update_conductor_table():
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE conductor ADD COLUMN phone TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE conductor ADD COLUMN joining_date TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE conductor ADD COLUMN status TEXT DEFAULT 'Active'")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
def update_conductor_table():
    conn = get_db()
    cursor = conn.cursor()

    columns = [row["name"] for row in cursor.execute("PRAGMA table_info(conductor)")]

    if "phone" not in columns:
        cursor.execute("ALTER TABLE conductor ADD COLUMN phone TEXT")

    if "joining_date" not in columns:
        cursor.execute("ALTER TABLE conductor ADD COLUMN joining_date TEXT")

    if "status" not in columns:
        cursor.execute("ALTER TABLE conductor ADD COLUMN status TEXT DEFAULT 'Active'")

    conn.commit()
    conn.close()



# -----------------------------
# Save Activity
# -----------------------------
def save_activity(activity):
    conn = get_db()
    cursor = conn.cursor()

    current_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")

    cursor.execute("""
        INSERT INTO activity(activity, activity_time)
        VALUES(?, ?)
    """, (activity, current_time))

    conn.commit()
    conn.close()
# -----------------------------
# Login Page
# -----------------------------
@app.route("/")
def index():
    return render_template("login.html")

# -----------------------------
# Login Validation
@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    print("Entered Username:", username)
    print("Entered Password:", password)

    if username == USERNAME and password == PASSWORD:
        session["logged_in"] = True
        return redirect(url_for("dashboard"))
    else:
        flash("❌ Invalid Username or Password")
        return redirect(url_for("index"))

# -----------------------------
# Dashboard
# -----------------------------
@app.route("/dashboard")
def dashboard():

    if not session.get("logged_in"):
        return redirect(url_for("index"))

    conn = get_db()
    cursor = conn.cursor()

    summary = get_dashboard_summary()

    # Dashboard Summary
    total_conductors = summary["total_conductors"]
    total_buses = summary["total_buses"]
    total_sr = summary["total_sr"]
    total_cash = summary["total_cash"]

    # Cash Status
    cursor.execute("SELECT COUNT(*) FROM cash WHERE status='Pending'")
    pending_cash = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM cash WHERE status='Completed'")
    completed_cash = cursor.fetchone()[0]

    # Today's Duties
    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "SELECT COUNT(*) FROM bus WHERE duty_date=?",
        (today,)
    )
    today_duties = cursor.fetchone()[0]

    # Bus Status
    cursor.execute("SELECT COUNT(*) FROM bus WHERE status='Running'")
    running_buses = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bus WHERE status='Maintenance'")
    maintenance_buses = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bus WHERE status='Available'")
    available_buses = cursor.fetchone()[0]

    # Recent Activities
    cursor.execute("""
        SELECT activity, activity_time
        FROM activity
        ORDER BY id DESC
        LIMIT 5
    """)
    activities = cursor.fetchall()

    conn.close()

    # Notifications
    notifications = []

    if pending_cash > 0:
        notifications.append(f"💰 {pending_cash} Cash Remittance(s) Pending")

    if maintenance_buses > 0:
        notifications.append(f"🛠 {maintenance_buses} Bus(es) Under Maintenance")

    if running_buses > 0:
        notifications.append(f"🚌 {running_buses} Bus(es) Running")

    if today_duties > 0:
        notifications.append(f"📅 {today_duties} Bus Allocation(s) Today")

    if total_cash > 50000:
        notifications.append(f"🏆 High Cash Collection ₹{total_cash}")

    current_date = datetime.now().strftime("%d %b %Y")
    current_time = datetime.now().strftime("%I:%M %p")

    # Dashboard Graph
    chart_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    chart_values = [12000, 18500, 9800, 15000, 21000, 17500, 23000]

    return render_template(
        "dashboard.html",
        total_conductors=total_conductors,
        total_buses=total_buses,
        total_sr=total_sr,
        total_cash=total_cash,
        current_date=current_date,
        current_time=current_time,
        pending_cash=pending_cash,
        completed_cash=completed_cash,
        today_duties=today_duties,
        running_buses=running_buses,
        maintenance_buses=maintenance_buses,
        available_buses=available_buses,
        chart_labels=chart_labels,
        chart_values=chart_values,
        activities=activities,
        notifications=notifications
    )

# -----------------------------
# Conductor Management
# -----------------------------
@app.route("/conductor")
def conductor():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM conductor ORDER BY employee_id")
    conductors = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM conductor WHERE shift='Morning'")
    morning_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM conductor WHERE shift='Afternoon'")
    afternoon_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM conductor WHERE shift='Night'")
    night_count = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "conductor.html",
        conductors=conductors,
        morning_count=morning_count,
        afternoon_count=afternoon_count,
        night_count=night_count
    )


# -----------------------------
# Save Conductor
# -----------------------------
@app.route("/save_conductor", methods=["POST"])
def save_conductor():
    try:
        print("FORM DATA:", request.form)

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO conductor
            (employee_id, name, depot, bus_number, route_number, shift)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            request.form["employee_id"],
            request.form["name"],
            request.form["depot"],
            request.form["bus_number"],
            request.form["route_number"],
            request.form["shift"]
        ))

        conn.commit()
        conn.close()

        flash("✅ Conductor Saved Successfully!")
        return redirect(url_for("conductor"))

    except Exception as e:
        print("ERROR:", e)
        return f"ERROR: {e}"




# -----------------------------
# Search Conductor
# -----------------------------
@app.route("/search_conductor")
def search_conductor():

    employee_id = request.args.get("employee_id")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM conductor WHERE employee_id LIKE ?",
        ('%' + employee_id + '%',)
    )

    conductors = cursor.fetchall()

    conn.close()

    return render_template("conductor.html", conductors=conductors)


# -----------------------------
# Edit Conductor
# -----------------------------
@app.route("/edit_conductor/<employee_id>")
def edit_conductor(employee_id):

    conn = get_db()
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


# -----------------------------
# Update Conductor
# -----------------------------
@app.route("/update_conductor", methods=["POST"])
def update_conductor():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE conductor
        SET
            name=?,
            depot=?,
            bus_number=?,
            route_number=?,
            shift=?
        WHERE employee_id=?
    """, (
        request.form["name"],
        request.form["depot"],
        request.form["bus_number"],
        request.form["route_number"],
        request.form["shift"],
        request.form["employee_id"]
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("conductor"))


# -----------------------------
# Delete Conductor
# -----------------------------
@app.route("/delete_conductor/<employee_id>")
def delete_conductor(employee_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM conductor WHERE employee_id=?",
        (employee_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("conductor"))
# -----------------------------
# Cash Remittance
# -----------------------------
@app.route("/cash")
def cash_page():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM cash
        ORDER BY id DESC
    """)

    cash_records = cursor.fetchall()

    cursor.execute("SELECT IFNULL(SUM(cash_amount),0) FROM cash")
    total_collection = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM cash WHERE status='Completed'")
    completed_cash = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM cash WHERE status='Pending'")
    pending_cash = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "cash.html",
        cash_records=cash_records,
        completed_cash=completed_cash,
        pending_cash=pending_cash,
        total_collection=total_collection
    )

# -----------------------------
# Save Cash
# -----------------------------
@app.route("/save_cash", methods=["POST"])
def save_cash():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cash
        (
            employee_id,
            conductor_name,
            bus_number,
            cash_amount,
            settlement_time,
            status,
            remarks
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        request.form["employee_id"],
        request.form["conductor_name"],
        request.form["bus_number"],
        request.form["cash_amount"],
        request.form["settlement_time"],
        request.form["status"],
        request.form["remarks"]
    ))

    conn.commit()

    save_activity(
    f"💰 Cash Submitted : {request.form['conductor_name']}"
)
    conn.close()

    flash("✅ Cash Saved Successfully!")

    return redirect(url_for("cash_page"))

@app.route("/edit_cash/<int:id>")
def edit_cash(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM cash WHERE id=?",
        (id,)
    )

    cash = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_cash.html",
        cash=cash
    )

@app.route("/update_cash", methods=["POST"])
def update_cash():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE cash
        SET
            employee_id=?,
            conductor_name=?,
            bus_number=?,
            cash_amount=?,
            settlement_time=?,
            status=?,
            remarks=?
        WHERE id=?
    """, (

        request.form["employee_id"],
        request.form["conductor_name"],
        request.form["bus_number"],
        request.form["cash_amount"],
        request.form["settlement_time"],
        request.form["status"],
        request.form["remarks"],
        request.form["id"]

    ))

    conn.commit()
    conn.close()

    return redirect(url_for("cash_page"))

@app.route("/delete_cash/<int:id>")
def delete_cash(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM cash WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("cash_page"))


# -----------------------------
# Search Cash
# -----------------------------
@app.route("/search_cash")
def search_cash():

    employee_id = request.args.get("employee_id")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM cash
        WHERE employee_id LIKE ?
        ORDER BY id DESC
    """, ('%' + employee_id + '%',))

    cash_records = cursor.fetchall()

    conn.close()

    return render_template(
        "cash.html",
        cash_records=cash_records
    )
# -----------------------------
# Bus Allocation
# -----------------------------
@app.route("/bus")
def bus():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM bus
        ORDER BY id DESC
    """)
    buses = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM bus WHERE status='Running'")
    running_buses = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bus WHERE status='Maintenance'")
    maintenance_buses = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bus WHERE status='Available'")
    available_buses = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "bus.html",
        buses=buses,
        running_buses=running_buses,
        maintenance_buses=maintenance_buses,
        available_buses=available_buses
    )

# -----------------------------
# Save Bus
# -----------------------------
@app.route("/save_bus", methods=["POST"])
def save_bus():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO bus
        (
            bus_number,
            route_number,
            driver_id,
            driver_name,
            conductor_id,
            conductor_name,
            shift,
            duty_date,
            status
        )
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        request.form["bus_number"],
        request.form["route"],
        request.form["driver_id"],
        request.form["driver_name"],
        request.form["conductor_id"],
        request.form["conductor_name"],
        request.form["shift"],
        request.form["duty_date"],
         request.form["status"]
    ))

    conn.commit()

    save_activity(
        f"🚌 Bus Allocated : {request.form['bus_number']}"
    )

    conn.close()

    flash("✅ Bus Allocated Successfully!")

    return redirect(url_for("bus"))

# -----------------------------
# Edit Bus
# -----------------------------
@app.route("/edit_bus/<int:id>")
def edit_bus(id):

    conn = get_db()
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

# -----------------------------
# Update Bus
# -----------------------------
@app.route("/update_bus", methods=["POST"])
def update_bus():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bus
        SET
            bus_number=?,
            route_number=?,
            driver_id=?,
            driver_name=?,
            conductor_id=?,
            conductor_name=?,
            shift=?,
            duty_date=?,
            status=?
        WHERE id=?
    """, (

        request.form["bus_number"],
        request.form["route_number"],
        request.form["driver_id"],
        request.form["driver_name"],
        request.form["conductor_id"],
        request.form["conductor_name"],
        request.form["shift"],
        request.form["duty_date"],
        request.form["status"],
        request.form["id"]

    ))

    conn.commit()
    conn.close()

    return redirect(url_for("bus"))
# -----------------------------
# Search Bus
# -----------------------------

@app.route("/search_bus")
def search_bus():

    bus_number = request.args.get("bus_number")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM bus
        WHERE bus_number LIKE ?
        ORDER BY id DESC
    """, ('%' + bus_number + '%',))

    buses = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM bus WHERE status='Running'")
    running_buses = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bus WHERE status='Maintenance'")
    maintenance_buses = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bus WHERE status='Available'")
    available_buses = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "bus.html",
        buses=buses,
        running_buses=running_buses,
        maintenance_buses=maintenance_buses,
        available_buses=available_buses
    )


# -----------------------------
# Delete Bus
# -----------------------------
@app.route("/delete_bus/<int:id>")
def delete_bus(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM bus WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("bus"))
# -----------------------------
# SR Entry
# -----------------------------
@app.route("/sr")
def sr():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM sr
        ORDER BY id DESC
    """)

    sr_records = cursor.fetchall()

    conn.close()

    return render_template(
        "sr.html",
        sr_records=sr_records
    )


# -----------------------------
# Save SR
# -----------------------------
# -----------------------------
# Save SR
# -----------------------------
@app.route("/save_sr", methods=["POST"])
def save_sr():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sr
        (
            sr_number,
            employee_id,
            conductor_name,
            bus_number,
            epos_collection,
            cash_collection,
            remarks
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        request.form["sr_number"],
        request.form["employee_id"],
        request.form["conductor_name"],
        request.form["bus_number"],
        request.form["epos_collection"],
        request.form["cash_collection"],
        request.form["remarks"]
    ))

    conn.commit()

    save_activity(
        f"📝 SR Entry Added : {request.form['sr_number']}"
    )

    conn.close()

    flash("✅ SR Saved Successfully!")

    return redirect(url_for("sr"))


@app.route("/edit_sr/<int:id>")
def edit_sr(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM sr WHERE id=?",
        (id,)
    )

    sr = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_sr.html",
        sr=sr
    )
@app.route("/update_sr", methods=["POST"])
def update_sr():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sr
        SET
            sr_number=?,
            employee_id=?,
            conductor_name=?,
            bus_number=?,
            epos_collection=?,
            cash_collection=?,
            remarks=?
        WHERE id=?
    """, (

        request.form["sr_number"],
        request.form["employee_id"],
        request.form["conductor_name"],
        request.form["bus_number"],
        request.form["epos_collection"],
        request.form["cash_collection"],
        request.form["remarks"],
        request.form["id"]

    ))

    conn.commit()
    conn.close()

    return redirect(url_for("sr"))
@app.route("/delete_sr/<int:id>")
def delete_sr(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM sr WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("sr"))


# -----------------------------
# Search SR
# -----------------------------
@app.route("/search_sr")
def search_sr():

    employee_id = request.args.get("employee_id")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM sr
        WHERE employee_id LIKE ?
        ORDER BY id DESC
    """, ('%' + employee_id + '%',))

    sr_records = cursor.fetchall()

    conn.close()

    return render_template(
        "sr.html",
        sr_records=sr_records
    )


# -----------------------------
# Reports
# -----------------------------
@app.route("/reports")
def reports():

    conn = get_db()
    cursor = conn.cursor()

    # Total Conductors
    cursor.execute("SELECT COUNT(*) FROM conductor")
    total_conductors = cursor.fetchone()[0]

    # Total Buses
    cursor.execute("SELECT COUNT(*) FROM bus")
    total_buses = cursor.fetchone()[0]

    # Total SR Entries
    cursor.execute("SELECT COUNT(*) FROM sr")
    total_sr = cursor.fetchone()[0]

    # Total Cash
    cursor.execute("SELECT IFNULL(SUM(cash_amount),0) FROM cash")
    total_cash = cursor.fetchone()[0]

    # Today's Cash
    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT IFNULL(SUM(cash_amount),0)
        FROM cash
        WHERE DATE(settlement_time)=?
    """, (today,))

    today_cash = cursor.fetchone()[0]

    # Highest Cash Collection
    cursor.execute("""
        SELECT conductor_name, cash_amount
        FROM cash
        ORDER BY cash_amount DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    if row:
        highest_conductor = row["conductor_name"]
        highest_cash = row["cash_amount"]
    else:
        highest_conductor = "N/A"
        highest_cash = 0

    # Weekly Chart
    cursor.execute("""
        SELECT settlement_time, cash_amount
        FROM cash
    """)

    rows = cursor.fetchall()

    week_data = defaultdict(int)

    for row in rows:
        try:
            date = datetime.strptime(
                row["settlement_time"],
                "%Y-%m-%dT%H:%M"
            )

            day = date.strftime("%a")
            week_data[day] += float(row["cash_amount"])

        except Exception as e:
            print("Date Error:", e)

    chart_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    chart_values = [
        week_data["Mon"],
        week_data["Tue"],
        week_data["Wed"],
        week_data["Thu"],
        week_data["Fri"],
        week_data["Sat"],
        week_data["Sun"]
    ]

    conn.close()

    return render_template(
        "reports.html",
        total_conductors=total_conductors,
        total_buses=total_buses,
        total_sr=total_sr,
        total_cash=total_cash,
        today_cash=today_cash,
        highest_conductor=highest_conductor,
        highest_cash=highest_cash,
        chart_labels=chart_labels,
        chart_values=chart_values
    )

    


 
# -----------------------------
# Download PDF Report
# -----------------------------
@app.route("/download_report")
def download_report():

    conn = get_db()
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

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=35,
        bottomMargin=35,
        leftMargin=40,
        rightMargin=40
    )

    styles = getSampleStyleSheet()

    title = styles["Title"]
    title.alignment = TA_CENTER
    title.textColor = colors.darkblue
    title.fontSize = 24

    heading = styles["Heading2"]
    heading.alignment = TA_CENTER
    heading.textColor = colors.HexColor("#1565C0")

    normal = styles["BodyText"]
    normal.fontSize = 11

    # ---------- Elements ----------
    elements = []

    elements.append(Paragraph("<b>RTC SMART DUTY SETTLEMENT SYSTEM</b>", title))
    elements.append(Paragraph("Management Report", heading))
    elements.append(Spacer(1, 0.25 * inch))

    report_id = "RTC-" + datetime.now().strftime("%Y%m%d")
    generated = datetime.now().strftime("%d-%b-%Y %I:%M %p")

    info = [
        ["Report ID", report_id],
        ["Generated On", generated],
        ["Prepared By", "RTC Administrator"]
    ]

    info_table = Table(info, colWidths=[130, 330])

    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#0D47A1")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("BACKGROUND", (1, 0), (1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(info_table)
    elements.append(Spacer(1, 0.30 * inch))

    summary = [
        ["Description", "Value"],
        ["Total Conductors", str(total_conductors)],
        ["Total Bus Allocations", str(total_buses)],
        ["Total SR Entries", str(total_sr)],
        ["Total Cash Collection", f"₹ {total_cash:,.2f}"]
    ]

    summary_table = Table(summary, colWidths=[320, 140])

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565C0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 0.30 * inch))

    elements.append(Paragraph(
        "<b>Remarks</b><br/>"
        "• This report is generated automatically from the RTC Smart Duty Settlement System.<br/>"
        "• The information shown above is based on the current database records.",
        normal
    ))

    elements.append(Spacer(1, 0.5 * inch))

    sign = Table([
        ["Prepared By", "Approved By"],
        ["__________________", "__________________"],
        ["RTC Administrator", "Depot Manager"]
    ], colWidths=[230, 230])

    sign.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(sign)
    elements.append(Spacer(1, 0.3 * inch))

    footer = Paragraph(
        "<font size='9' color='grey'>Generated by RTC Smart Duty Settlement System © 2026</font>",
        normal
    )

    elements.append(footer)

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=RTC_Management_Report.pdf"

    return response
# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully!")

    return redirect(url_for("index"))
# -----------------------------
# Run Application
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)

