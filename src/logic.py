"""All """
import csv, os
from tkinter import messagebox
from datetime import datetime

from utils import *

# In-Memory Data
patients = []  
served   = [] 
counter  = [1]

appointments  = []
activity_log  = []   
announcements = []  
staff_accounts = {}
login_attempts = {}  
current_user   = [""]
absent        = []   
last_called = [None]

def register_patient_full(name, age, gender, contact, complaint, arrived, category):
    pid = make_id()
    patients.append({
        "id": pid, 
        "name": name.title(), 
        "age": age,
        "gender": gender, 
        "contact": contact,
        "complaint": complaint.capitalize(),
        "arrived": arrived, 
        "category": category,
        "queue_no": len(patients) + len(served) + 1,
        "status": "Waiting",
        "visits": count_visits(name.title()),
        "reg_date": datetime.now().strftime("%d/%m/%Y") 
    })
    sort_patients()
    return pid

def sort_patients():
    patients.sort(key=lambda p: (PRIORITY[p["category"]], p["arrived"]))

def save_staff_accounts():    
    with open(STAFF_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["username", 
                                               "password_hash", 
                                               "role"])
        writer.writeheader()
        for u, v in staff_accounts.items():
            writer.writerow({
                "username":      u,
                "password_hash": v["password_hash"],
                "role":          v["role"]
            })

def load_staff_accounts():    
    if not os.path.exists(STAFF_FILE):
        return
    with open(STAFF_FILE) as f:
        for row in csv.DictReader(f):
            staff_accounts[row["username"]] = {
                "password_hash": row["password_hash"],
                "role":          row["role"]
            }

def reorder_queue():    
    for i, p in enumerate(patients, 1):
        p["queue_no"] = i

def call_next_patient():
    if not patients:
        return None
    p = patients.pop(0)
    p["status"] = "Served"
    served.append(p)
    last_called[0] = p
    return p

def undo_last_call():
    if last_called[0] is None:
        return False
    p = last_called[0]
    if p in served:
        served.remove(p)
        p["status"] = "Waiting" 
        patients.append(p)
        sort_patients()         
        last_called[0] = None
        return True
    return False

def update_patient(pid, name, age, gender, contact, complaint, arrived, category):
    for p in patients:
        if p["id"] == pid:
            p["name"] = name.title(); 
            p["age"] = age
            p["gender"] = gender;     
            p["contact"] = contact
            p["complaint"] = complaint.capitalize()
            p["arrived"] = arrived;   
            p["category"] = category
            break
    sort_patients()

def delete_patient(pid):
    global patients
    patients[:] = [p for p in patients if p["id"] != pid]
    reorder_queue() 

def make_id():
    pid = f"P-{counter[0]:03d}"
    counter[0] += 1
    return pid

def find_by_id(pid):
    for p in patients + served:
        if p["id"] == pid.upper().strip():
            return p
    return None

def search_patients(term):
    term = term.lower()
    return [p for p in patients + served
            if term in p["id"].lower() or term in p["name"].lower()]

def queue_summary():
    counts = {"Emergency": 0, "Pregnant": 0, "Normal": 0}
    for p in patients:
        counts[p["category"]] += 1
    return counts

def served_summary():
    counts = {"Emergency": 0, "Pregnant": 0, "Normal": 0}
    for p in served:
        counts[p["category"]] += 1
    return counts

def count_visits(name):    
    return sum(1 for p in served if p["name"] == name)

def check_duplicate(name, contact):    
    name = name.title()
    for p in patients:
        if p["name"] == name and p.get("contact", "") == contact:
            return True
    return False

# Added - Staff Activity Log 
def log_activity(message):
    timestamp = datetime.now().strftime("%H:%M")
    activity_log.append(f"{timestamp} {message}")
    save_activity_log()

def save_activity_log():
    with open(ACTIVITY_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["entry"])
        for entry in activity_log:
            writer.writerow([entry])

def load_activity_log():
    if not os.path.exists(ACTIVITY_FILE):
        return
    activity_log.clear() 
    with open(ACTIVITY_FILE) as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if row:
                activity_log.append(row[0])

def save_announcements():
    with open(ANNOUNCEMENTS_FILE, "w") as f:
        for a in announcements:
            f.write(a + "\n")

def load_announcements():
    if not os.path.exists(ANNOUNCEMENTS_FILE):
        return
    announcements.clear() 
    with open(ANNOUNCEMENTS_FILE) as f:
        for line in f:
            line = line.rstrip("\n")
            if line:
                announcements.append(line)

# Added - Waiting Time Alerts
def get_overdue_patients():
    overdue = []
    for i, p in enumerate(patients, 1):
        if i * AVG_MIN >= WAIT_ALERT_MIN:
            overdue.append(p)
    return overdue

def book_appointment(name, contact, date, time, note, staff_user):
    appointments.append({
        "name": name.title(), 
        "contact": contact,
        "date": date, 
        "time": time, 
        "note": note,
        "booked_by": staff_user
    })
    save_appointments()
    log_activity(f"{staff_user} booked appointment for {name.title()} on {date} {time}")

def save_appointments():
    with open(APPOINTMENTS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=APPT_FIELDS)
        writer.writeheader()
        for a in appointments:
            writer.writerow(a)

def load_appointments():
    if not os.path.exists(APPOINTMENTS_FILE):
        return
    appointments.clear()
    with open(APPOINTMENTS_FILE) as f:
        for row in csv.DictReader(f):
            appointments.append(row)

def get_appointments_for_today():
    today = datetime.now().strftime("%d/%m/%Y")
    return [a for a in appointments if a["date"] == today]

# Added - Nurse Assignment
def assign_nurse(pid, nurse_name):
    for p in patients:
        if p["id"] == pid:
            p["assigned_nurse"] = nurse_name
            log_activity(f"{pid} assigned to {nurse_name}")
            return True
    return False

# Added - Search by Date
def search_by_date(date_str):
    return [p for p in patients + served if p.get("reg_date") == date_str]

# Added - Registration Cancellation Reasons
cancellation_reasons = []

def record_cancellation(pid, name, reason):
    cancellation_reasons.append({"id": pid, 
                                 "name": name, 
                                 "reason": reason})
    log_activity(f"{current_user[0]} cancelled {pid} ({name}) - reason: {reason}")

# Added - Patient Recall / Absent Patient Management
def mark_absent(pid):
    global patients
    target = next((p for p in patients if p["id"] == pid), None)
    if not target:
        return False
    target["status"] = "Absent"
    absent.append(target)
    patients[:] = [p for p in patients if p["id"] != pid]
    reorder_queue()
    log_activity(f"{current_user[0]} marked {pid} ({target['name']}) as absent")
    return True

def recall_patient(pid):
    global absent
    target = next((p for p in absent if p["id"] == pid), None)
    if not target:
        return False
    target["status"] = "Waiting"
    patients.append(target)
    sort_patients()
    absent[:] = [p for p in absent if p["id"] != pid]
    log_activity(f"{current_user[0]} recalled {pid} ({target['name']})")
    return True

# CSV & Export Backup
def export_served_csv():
    filename = "served_patients.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for p in served:
            row = {k: p.get(k, "") for k in FIELDNAMES}
            row["status"] = "Served"
            writer.writerow(row)
    return filename

def export_daily_report():
    filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.txt"
    counts = queue_summary()
    with open(filename, "w") as f:
        f.write("Daily Report\n")
        f.write(f"Date: {datetime.now().strftime('%d/%m/%Y')}\n\n")
        f.write(f"Registered: {len(patients) + len(served)}\n")
        f.write(f"Served    : {len(served)}\n")
        f.write(f"Emergency : {counts['Emergency']}\n")
        f.write(f"Pregnant  : {counts['Pregnant']}\n")
        f.write(f"Normal    : {counts['Normal']}\n")
        f.write(f"Absent    : {len(absent)}\n")
    return filename

SESSION_FILE = "session_backup.csv"

def save_session():
    save_to_csv(SESSION_FILE)

def load_session():
    if not os.path.exists(SESSION_FILE):
        return
    import_backup(SESSION_FILE)

def save_to_csv(filename):
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for p in patients:
            row = {k: p.get(k, "") for k in FIELDNAMES}
            row["status"] = "Waiting"
            writer.writerow(row)
        for p in served:
            row = {k: p.get(k, "") for k in FIELDNAMES}
            row["status"] = "Served"
            writer.writerow(row)

def export_csv():
    save_to_csv("export.csv")
    messagebox.showinfo("Exported", "Records saved to export.csv")

def auto_backup():
    date_str = datetime.now().strftime("%Y_%m_%d")
    save_to_csv(f"backup_{date_str}.csv")

def import_backup(filepath):
    global patients, served
    patients.clear(); served.clear()
    with open(filepath) as f:
        for row in csv.DictReader(f):
            row["age"]      = int(row["age"])      if row["age"].isdigit()      else 0
            row["queue_no"] = int(row["queue_no"]) if row["queue_no"].isdigit() else 0
            if row["status"] == "Waiting":
                patients.append(row)
            else:
                served.append(row)
    sort_patients()