""" Patient Queue Management System - MediCare Community Clinic, Sierra Leone
GUI: ttkbootstrap (flatly theme)
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
import csv,os

# In-Memory Data
patients = []   # list of patient dicts
served   = []   # list of served patient dicts
counter  = [1]  # patient ID counter

PRIORITY = {"Emergency": 1, "Pregnant": 2, "Normal": 3}

# Core function 

def make_id():
    pid = f"P-{counter[0]:03d}"
    counter[0] += 1
    return pid

def sort_patients():
    patients.sort(key=lambda p: (PRIORITY[p["category"]], p["arrived"]))

def register_patient(name, age, complaint, arrived, category):
    pid = make_id()
    patients.append({
        "id": pid, "name": name.title(), "age": age,
        "complaint": complaint.capitalize(),
        "arrived": arrived, "category": category,
        "queue_no": len(patients) + len(served) + 1
    })
    sort_patients()
    return pid

def call_next_patient():
    if not patients:
        return None
    p = patients.pop(0)
    served.append(p)
    return p

def search_patients(term):
    term = term.lower()
    return [p for p in patients + served
            if term in p["id"].lower() or term in p["name"].lower()]

def queue_summary():
    counts = {"Emergency": 0, "Pregnant": 0, "Normal": 0}
    for p in patients:
        counts[p["category"]] += 1
    return counts

#  Validation

def ok_name(t):  return bool(t.strip()) and t.replace(" ", "").isalpha()
def ok_age(t):   return t.isdigit() and 0 <= int(t) <= 120
def ok_note(t):  return bool(t.strip()) and not t.strip().isdigit()
def ok_time(t):
    return (len(t) == 5 and t[2] == ":" and t[:2].isdigit() and t[3:].isdigit()
            and 0 <= int(t[:2]) <= 23 and 0 <= int(t[3:]) <= 59)

#  Added - staff accounts (receptionist + nurse) 
staff_accounts = {}

last_called = [None]

# Added - avg minutes per patient for wait estimate
AVG_MIN = 5

def ok_complaint(t): 
    """Complaint must be at least 3 characters and not purely numeric"""
    return bool(t.strip()) and not t.strip().isdigit() and len(t.strip()) >= 3

def ok_contact(t):
    """Contact must be digits only, 7-15 characters""" 
    return t.isdigit() and 7 <= len(t) <= 15

# Added - gender & contact stored on patient
def register_patient_full(name, age, gender, contact, complaint, arrived, category):
    pid = make_id()
    patients.append({
        "id": pid, "name": name.title(), "age": age,
        "gender": gender, "contact": contact,
        "complaint": complaint.capitalize(),
        "arrived": arrived, "category": category,
        "queue_no": len(patients) + len(served) + 1
    })
    sort_patients()
    return pid

# Added - undo last called patient
def undo_last_call():
    if last_called[0] is None:
        return False
    p = last_called[0]
    if p in served:
        served.remove(p)
        patients.insert(0, p)
        last_called[0] = None
        return True
    return False

# Addded - edit existing patient 
def update_patient(pid, name, age, gender, contact, complaint, arrived, category):
    for p in patients:
        if p["id"] == pid:
            p["name"] = name.title(); p["age"] = age
            p["gender"] = gender;     p["contact"] = contact
            p["complaint"] = complaint.capitalize()
            p["arrived"] = arrived;   p["category"] = category
            break
    sort_patients()

# Added - delete patient by ID
def delete_patient(pid):
    global patients
    patients = [p for p in patients if p["id"] != pid]

# Added - exact ID lookup
def find_by_id(pid):
    for p in patients + served:
        if p["id"] == pid.upper().strip():
            return p
    return None

# Added - served breakdown by category
def served_summary():
    counts = {"Emergency": 0, "Pregnant": 0, "Normal": 0}
    for p in served:
        counts[p["category"]] += 1
    return counts

# Added - CSV export & auto backup
FIELDNAMES = ["id","name","age","gender","contact","complaint",
              "arrived","category","queue_no","status"]

def save_to_csv(filename):
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for p in patients:
            row = {k: p.get(k, "") for k in FIELDNAMES}; row["status"] = "Waiting"
            writer.writerow(row)
        for p in served:
            row = {k: p.get(k, "") for k in FIELDNAMES}; row["status"] = "Served"
            writer.writerow(row)

def export_csv():
    save_to_csv("export.csv")
    messagebox.showinfo("Exported", "Records saved to export.csv")

def auto_backup():
    """Automatically save a dated backup file when the program closes"""
    date_str = datetime.now().strftime("%Y_%m_%d")
    save_to_csv(f"backup_{date_str}.csv")

# Added - Login Screen (built inside the single root window)
def show_login_screen(root, on_success):
    root.title("MediQueue - Staff Login")
    root.geometry("600x620")
    root.resizable(False, False)
    try: root.state("normal")
    except: pass

    win = ttk.Frame(root)
    win.pack(fill=BOTH, expand=True)

    ttk.Label(win, text="Welcome to MediCare SDG 3",
              font=("Tahoma", 16, "bold"),
              bootstyle="primary").pack(pady=(36, 2))
    ttk.Label(win, text="Patient Queue System",
              font=("Tahoma", 13),
              bootstyle="primary").pack()
    ttk.Label(win, text="Receptionist & Nurse Staff Login",
              font=("Tahoma", 10),
              bootstyle="secondary").pack(pady=(6, 18))
    ttk.Separator(win).pack(fill=X, padx=40, pady=(0, 20))

    frm = ttk.Frame(win, padding=(40, 0)); frm.pack()

    uv = tk.StringVar(); pv = tk.StringVar()
    rv = tk.StringVar(value="Receptionist")

    for i, (lbl, var, show) in enumerate([
        ("Username", uv, ""),
        ("Password", pv, "*"),
    ]):
        ttk.Label(frm, text=f"{lbl}:", font=("Tahoma", 11)).grid(
            row=i, column=0, sticky=W, pady=12)
        ttk.Entry(frm, textvariable=var, show=show, width=28,
                  font=("Tahoma", 11)).grid(
            row=i, column=1, pady=12, padx=(12, 0))

    ttk.Label(frm, text="Role:", font=("Tahoma", 11)).grid(
        row=2, column=0, sticky=W, pady=12)
    ttk.Combobox(frm, textvariable=rv, width=26, state="readonly",
                 values=["Receptionist", "Nurse"],
                 font=("Tahoma", 11)).grid(
        row=2, column=1, pady=12, padx=(12, 0))

    err = ttk.Label(frm, text="", bootstyle="danger",
                    font=("Tahoma", 9), wraplength=380)
    err.grid(row=3, column=0, columnspan=2, pady=8)

    def do_login():
        u, p, r = uv.get().strip(), pv.get(), rv.get()
        if not u or not p:
            err.config(text="Please enter your username and password"); return
        if u not in staff_accounts:
            err.config(text="Username not found. Register first"); return
        if staff_accounts[u]["password"] != p:
            err.config(text="Incorrect password."); return
        if staff_accounts[u]["role"] != r:
            err.config(text=f"This account is registered as {staff_accounts[u]['role']}"); return
        win.destroy()          
        on_success(root, u, r)

    def do_register():
        u, p, r = uv.get().strip(), pv.get(), rv.get()
        if not u or not p:
            err.config(text="Enter a username and password to register"); return
        if len(p) < 4:
            err.config(text="Password must be at least 4 characters"); return
        if u in staff_accounts:
            err.config(text="Username already taken. Choose another"); return
        staff_accounts[u] = {"password": p, "role": r}
        err.config(text=f"{r} '{u}' registered successfully, You can now log in")

    btn = ttk.Frame(frm)
    btn.grid(row=4, column=0, columnspan=2, pady=20)
    ttk.Button(btn, text="Login",    command=do_login,
               bootstyle="primary",         width=16).pack(side=LEFT, padx=10)
    ttk.Button(btn, text="Register", command=do_register,
               bootstyle="success-outline", width=16).pack(side=LEFT, padx=10)

# Added - Edit / Delete Dashboard
def open_edit_dashboard(parent):
    win = ttk.Toplevel(parent)
    win.title("Edit / Delete Patient")
    win.geometry("500x580")
    win.grab_set()

    ttk.Label(win, text="Edit or Delete Patient Record",
              font=("Tahoma", 12, "bold")).pack(pady=10)
    ttk.Separator(win).pack(fill=X, padx=10)

    top = ttk.Frame(win, padding=(16, 10)); top.pack(fill=X)
    ttk.Label(top, text="Search by Patient ID:").pack(side=LEFT, padx=(0, 8))
    sid = tk.StringVar()
    ttk.Entry(top, textvariable=sid, width=14).pack(side=LEFT)

    frm = ttk.Frame(win, padding=16); frm.pack(fill=BOTH, expand=True)

    nv = tk.StringVar(); av = tk.StringVar()
    gv = tk.StringVar(value="Male"); ctv = tk.StringVar()
    cv = tk.StringVar(); tv = tk.StringVar()
    kv = tk.StringVar(value="Normal")

    for i, (lbl, var) in enumerate([("Full Name", nv), ("Age", av),
                                     ("Contact", ctv), ("Complaint", cv),
                                     ("Arrived (HH:MM)", tv)]):
        ttk.Label(frm, text=f"{lbl}:").grid(row=i, column=0, sticky=W, pady=5)
        ttk.Entry(frm, textvariable=var, width=28).grid(
            row=i, column=1, pady=5, padx=(8, 0))

    ttk.Label(frm, text="Gender:").grid(row=5, column=0, sticky=W, pady=5)
    ttk.Combobox(frm, textvariable=gv, width=26, state="readonly",
                 values=["Male", "Female"]).grid(row=5, column=1, pady=5, padx=(8, 0))

    ttk.Label(frm, text="Category:").grid(row=6, column=0, sticky=W, pady=5)
    ttk.Combobox(frm, textvariable=kv, width=26, state="readonly",
                 values=["Emergency", "Pregnant", "Normal"]).grid(
                 row=6, column=1, pady=5, padx=(8, 0))

    err   = ttk.Label(frm, text="", bootstyle="danger", font=("Tahoma", 9))
    err.grid(row=7, column=0, columnspan=2, pady=2)
    found = [None]

    def do_search():
        p = find_by_id(sid.get())
        if not p: err.config(text="Patient ID not found"); return
        if p in served: err.config(text="Cannot edit a served patient"); return
        found[0] = p
        nv.set(p["name"]); av.set(str(p["age"]))
        gv.set(p.get("gender", "Male")); ctv.set(p.get("contact", ""))
        cv.set(p["complaint"]); tv.set(p["arrived"]); kv.set(p["category"])
        err.config(text="")

    def do_update():
        if not found[0]: err.config(text="Search for a patient first"); return
        n, a, ct, c, t, g, k = (nv.get().strip(), av.get().strip(),
                                  ctv.get().strip(), cv.get().strip(),
                                  tv.get().strip(), gv.get(), kv.get())
        for ok, msg in [(ok_name(n),   "Name: letters only"),
                        (ok_age(a),    "Age: 0 to 120"),
                        (ok_note(c),   "Enter a valid complaint"),
                        (ok_time(t),   "Time must be HH:MM")]:
            if not ok: err.config(text=msg); return
        if g == "Male" and k == "Pregnant":
            err.config(text="Male cannot be categorised as Pregnant"); return
        update_patient(found[0]["id"], n, int(a), g, ct, c, t, k)
        messagebox.showinfo("Updated", f"Patient {found[0]['id']} updated")
        win.destroy()

    def do_delete():
        if not found[0]: err.config(text="Search for a patient first"); return
        pid = found[0]["id"]
        if messagebox.askyesno("Confirm Delete",
            f"Delete {pid} — {found[0]['name']}?\nThis cannot be undone"):
            delete_patient(pid)
            messagebox.showinfo("Deleted", f"Patient {pid} removed")
            win.destroy()

    ttk.Button(top, text="Search", command=do_search,
               bootstyle="info", width=10).pack(side=LEFT, padx=8)

    btn = ttk.Frame(win); btn.pack(pady=6)
    ttk.Button(btn, text="Update", command=do_update,
               bootstyle="primary",          width=14).pack(side=LEFT, padx=6)
    ttk.Button(btn, text="Delete", command=do_delete,
               bootstyle="danger-outline",   width=14).pack(side=LEFT, padx=6)
    ttk.Button(btn, text="Cancel", command=win.destroy,
               bootstyle="secondary-outline",width=10).pack(side=LEFT, padx=6)

# Dashbords

def open_queue_dashboard(parent):
    win = ttk.Toplevel(parent)
    win.title("Live Queue")
    win.geometry("1100x650")

    ttk.Label(win, text="Waiting Queue", font=("Tahoma", 13, "bold"),
              bootstyle="primary").pack(pady=(10, 2))
    ttk.Separator(win).pack(fill=X, padx=10)

    cols   = ("#", "ID", "Name", "Age", "Category", "Arrived", "Complaint", "Est. Wait") 
    widths = [50,   70,   150,    50,      100,       80,         170,           90]

    frame = ttk.Frame(win); frame.pack(fill=BOTH, expand=True, padx=10, pady=8)
    tree = ttk.Treeview(frame, columns=cols, show="headings", height=12)
    for c, w in zip(cols, widths):
        tree.heading(c, text=c)
        tree.column(c, width=w, anchor=CENTER, minwidth=60, stretch=True)
    tree.column("Name",      anchor=W, stretch=True)
    tree.column("Complaint", anchor=W, stretch=True)
    sb = ttk.Scrollbar(frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side=LEFT, fill=BOTH, expand=True); sb.pack(side=LEFT, fill=Y)

    s = ttk.Style()
    s.configure("Queue.Treeview.Heading", background="#1a4f8a", foreground="white", font=("Tahoma", 10, "bold"), relief="flat")
    s.map("Queue.Treeview.Heading", background=[("active","#1a4f8a")])
    tree.configure(style="Queue.Treeview")
    tree.tag_configure("next",  background="#c8f0d4", foreground="#1a4731")
    tree.tag_configure("emerg", background="#fad4d4", foreground="#6b1a1a")
    tree.tag_configure("preg",  background="#d6eaf8", foreground="#1a3a5c")

    ttk.Label(win, text="Green = Next   Red = Emergency   Blue = Pregnant",
              font=("Tahoma", 9), bootstyle="secondary").pack(anchor=W, padx=12)

    def refresh():
        tree.delete(*tree.get_children())
        if not patients:
            tree.insert("", END, values=("-", "-", "No patients waiting", "-", "-", "-", " -", "-"))
        else:
            for i, p in enumerate(patients, 1):
                tag = ("next" if i == 1 else
                   "emerg" if p["category"] == "Emergency" else
                   "preg"  if p["category"] == "Pregnant"  else "")
            wait = f"{i * AVG_MIN} min" 
            tree.insert("", END, values=(i, p["id"], p["name"], p["age"],
                        p["category"], p["arrived"], p["complaint"], wait), tags=(tag,))
            
            if win.winfo_exists():
                win.after(10000, refresh)

    def undo_call():  # Added - restore accidental call
        if undo_last_call():
            messagebox.showinfo("Restored", "Last called patient returned to queue")
            refresh()
        else:
            messagebox.showwarning("Nothing to Undo", "No recent call to restore")        

    def call_next():
        if not patients:
            messagebox.showinfo("Empty", "No patients in queue."); return
        p = patients[0]
        if not messagebox.askyesno("Call Next",
            f"Call: {p['name']}  ({p['category']})\nComplaint: {p['complaint']}"): return
        called = call_next_patient()
        last_called[0] = called
        nxt = (f"Next: {patients[0]['name']} ({patients[0]['category']})" 
                if patients else "Queue is now empty")
        messagebox.showinfo("Now Calling",
            f"{called['name'].upper()} - Ticket #{called['queue_no']}\n"
            f"Category : {called['category']}\nComplaint: {called['complaint']}\n\n{nxt}")
        refresh()

# Remove duplicate button row
    btn = ttk.Frame(win); btn.pack(pady=8)
    ttk.Button(btn, text="Call Next",  command=call_next,
               bootstyle="success",         width=14).pack(side=LEFT, padx=5)
    ttk.Button(btn, text="Undo Call",  command=undo_call,      
               bootstyle="warning-outline", width=14).pack(side=LEFT, padx=5)
    ttk.Button(btn, text="Refresh",    command=refresh,
               bootstyle="info-outline",    width=12).pack(side=LEFT, padx=5)
    ttk.Button(btn, text="Close",      command=win.destroy,
               bootstyle="secondary-outline", width=10).pack(side=LEFT, padx=5)
    refresh()


def open_register_dashboard(parent, on_done):
    win = ttk.Toplevel(parent)
    win.title("Register Patient")
    win.geometry("480x520")
    win.grab_set()

    ttk.Label(win, text="Register New Patient",
              font=("Tahoma", 12, "bold")).pack(pady=10)
    ttk.Separator(win).pack(fill=X, padx=10)

    frm = ttk.Frame(win, padding=16); frm.pack(fill=BOTH, expand=True)

    nv = tk.StringVar();  av  = tk.StringVar()
    gv = tk.StringVar(value = "Male")
    ctv = tk.StringVar()
    cv = tk.StringVar() 
    tv = tk.StringVar(value=datetime.now().strftime("%H:%M"))
    kv = tk.StringVar(value="Normal")

    for i, (lbl, var) in enumerate([("Full Name", nv), 
                                     ("Age", av),
                                     ("Contact Number", ctv),
                                     ("Complaint", cv), 
                                     ("Arrived (HH:MM)", tv)]):
        ttk.Label(frm, text=f"{lbl}:").grid(row=i, column=0, sticky=W, pady=5)
        ttk.Entry(frm, textvariable=var, width=28).grid(
            row=i, column=1, pady=6, padx=(8, 0))

    ttk.Label(frm, text="Gender:").grid(row=5, column=0, sticky=W, pady=5)
    gender_cb = ttk.Combobox(frm, textvariable=gv, width=26, state="readonly", 
                             values=["Male", "Female"])
    gender_cb.grid(row=5, column=1, pady=5, padx=(8, 0))

    # Category now uses row 6
    ttk.Label(frm, text="Category:").grid(row=6, column=0, sticky=W, pady=5)
    cat_cb = ttk.Combobox(frm, textvariable=kv, width=26, state="readonly",
                 values=["Emergency", "Pregnant", "Normal"])
    cat_cb.grid(row=6, column=1, pady=5, padx=(8, 0))

    # error label moved to row 7 (was overlapping gender_cb)
    err = ttk.Label(frm, text="", bootstyle="danger", font=("Tahoma", 9))
    err.grid(row=7, column=0, columnspan=2, pady=2)

    def on_gender_change(*_):  # Added - block male from Pregnant
        if gv.get() == "Male":
            cat_cb.config(values=["Emergency", "Normal"])
            if kv.get() == "Pregnant": kv.set("Normal")
        else:
            cat_cb.config(values=["Emergency", "Pregnant", "Normal"])
    gv.trace_add("write", on_gender_change)

    def submit():
        n, a, ct, c, t, k = (nv.get().strip(), av.get().strip(),
                              ctv.get().strip(), cv.get().strip(), 
                              tv.get().strip(), kv.get())
        for ok, msg in [(ok_name(n), "Name: letters only"),
                        (ok_age(a),  "Age: 0-120"),
                        (ok_contact(ct),  "Contact: digits only, 7-15 numbers"),  
                        (ok_complaint(c), "Complaint: at least 3 characters"),  
                        (ok_time(t), "Time must be HH:MM")]:
            if not ok: err.config(text=msg); return

        pid = register_patient_full(n, int(a), gv.get(), ct, c, t, k) 
        pos  = next((i+1 for i, p in enumerate(patients) if p["id"] == pid), "?")
        wait = pos * AVG_MIN if isinstance(pos, int) else "?"
        messagebox.showinfo("Registered",
            f"Name     : {n.title()}\nID       : {pid}\n"
            f"Category : {k}\nPosition : {pos} of {len(patients)}\n"
            f"Est. Wait: {wait} min") 
        on_done(); win.destroy()

    ttk.Button(frm, text="Register Patient", command=submit,
               bootstyle="success", width=18).grid(
               row=8, column=0, columnspan=2, pady=10)


def open_search_dashboard(parent):
    win = ttk.Toplevel(parent)
    win.title("Search Patient")
    win.geometry("1100x620")

    ttk.Label(win, text="Search Patient", font=("Tahoma", 13, "bold"),
              bootstyle="primary").pack(pady=(10, 2))
    ttk.Separator(win).pack(fill=X, padx=10, pady=(0, 8))

    bar = ttk.Frame(win); bar.pack(fill=X, padx=10)
    ttk.Label(bar, text="Name or ID:").pack(side=LEFT, padx=(0, 8))
    sv = tk.StringVar()
    ttk.Entry(bar, textvariable=sv, width=34).pack(side=LEFT)

    cols   = ("ID", "Name", "Age", "Category", "Arrived", "Complaint", "Status")
    widths = [90,   150,    60,    110,        90,        160,         80]
    frame  = ttk.Frame(win); frame.pack(fill=BOTH, expand=True, padx=10, pady=8)
    s2 = ttk.Style()
    s2.configure("Search.Treeview.Heading", background="#0d6eaa", foreground="white",
                 font=("Tahoma", 10, "bold"), relief="flat")
    s2.map("Search.Treeview.Heading", background=[("active", "#0d6eaa")])
    s2.configure("Search.Treeview", rowheight=26)
    tree   = ttk.Treeview(frame, columns=cols, show="headings", 
                          height=12, style="Search.Treeview")
    
    for c, w in zip(cols, widths):
        tree.heading(c, text=c); 
        tree.column(c, width=w, anchor=CENTER, minwidth=60, stretch=True)
    tree.column("Name",      anchor=W, stretch=True)
    tree.column("Complaint", anchor=W, stretch=True)
    sb = ttk.Scrollbar(frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side=LEFT, fill=BOTH, expand=True); sb.pack(side=LEFT, fill=Y)

    info = ttk.Label(win, text="Type to search…", bootstyle="secondary")
    info.pack(anchor=W, padx=12, pady=4)

    def do_search(*_):
        term = sv.get().strip()
        tree.delete(*tree.get_children())
        if not term: info.config(text="Type to search…"); return
        res = search_patients(term)
        for p in res:
            status = "Waiting" if p in patients else "Served"
            tree.insert("", END, values=(p["id"], p["name"], p["age"],
                        p["category"], p["arrived"], p["complaint"], status))
        info.config(text=f"{len(res)} result(s) found." if res 
                    else f"No match for '{term}'.")

    sv.trace_add("write", do_search)
    ttk.Button(win, text="Close", command=win.destroy,
               bootstyle="secondary-outline", width=10).pack(pady=6)


def open_served_dashboard(parent):
    win = ttk.Toplevel(parent)
    win.title("Served Patients")
    win.geometry("1100x620")

    ttk.Label(win, text=f"Served Today - {len(served)} patient(s)",
              font=("Tahoma", 13, "bold"), bootstyle="success").pack(pady=(10, 2))
    ttk.Separator(win).pack(fill=X, padx=10, pady=(0, 8))

    cols   = ("ID", "Name", "Age", "Category", "Arrived", "Complaint")
    widths = [90,   150,    60,    110,        90,        200]
    frame  = ttk.Frame(win); frame.pack(fill=BOTH, expand=True, padx=10)

    s3 = ttk.Style()
    s3.configure("Served.Treeview.Heading", background="#198754", foreground="white",
                 font=("Tahoma", 10, "bold"), relief="flat")
    s3.map("Served.Treeview.Heading", background=[("active", "#198754")])
    s3.configure("Served.Treeview", rowheight=28)

    tree = ttk.Treeview(frame, columns=cols, show="headings",
                        height=14, style="Served.Treeview")
    for c, w in zip(cols, widths):
        tree.heading(c, text=c)
        tree.column(c, width=w, anchor=CENTER, minwidth=60, stretch=True)
    tree.column("Name",      anchor=W, stretch=True)
    tree.column("Complaint", anchor=W, stretch=True)

    # Alternating row colours for readability
    tree.tag_configure("odd",  background="#f7fbf7", foreground="#1a1a1a")
    tree.tag_configure("even", background="#e8f5e9", foreground="#1a1a1a")

    sb = ttk.Scrollbar(frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side=LEFT, fill=BOTH, expand=True); sb.pack(side=LEFT, fill=Y)

    def load_served():
        tree.delete(*tree.get_children())
        if not served:
            tree.insert("", END, values=("—","No patients served yet","—","—","—","—"))
            return
        for i, p in enumerate(served):
            tag = "odd" if i % 2 == 0 else "even"
            tree.insert("", END, values=(p["id"], p["name"], p["age"],
                        p["category"], p["arrived"], p["complaint"]), tags=(tag,))

    def clear_served(): 
        if not served:
            messagebox.showinfo("Empty", "No served patients to clear"); return
        if messagebox.askyesno("Confirm Clear",
            f"Clear all {len(served)} served records?\nThis cannot be undone"):
            served.clear()
            last_called[0] = None
            load_served()
            messagebox.showinfo("Cleared", "Served patients list cleared")

    load_served()
    btn = ttk.Frame(win); btn.pack(pady=8)
    ttk.Button(btn, text="Clear Served", command=clear_served,  
               bootstyle="danger-outline",   width=16).pack(side=LEFT, padx=6)
    ttk.Button(btn, text="Export CSV",   command=export_csv,   
               bootstyle="success-outline",  width=14).pack(side=LEFT, padx=6)
    ttk.Button(btn, text="Close",        command=win.destroy,
               bootstyle="secondary-outline", width=10).pack(side=LEFT, padx=6)


def open_summary_dashboard(parent):
    win = ttk.Toplevel(parent)
    win.title("Summary")
    win.geometry("580x560")

    ttk.Label(win, text="Today's Summary", font=("Tahoma", 13, "bold"),
              bootstyle="primary").pack(pady=(10, 2))
    ttk.Separator(win).pack(fill=X, padx=10, pady=(0, 10))

    counts  = queue_summary()
    scounts = served_summary() 
    avg_w   = round(len(patients) / max(1, len(patients) + len(served)), 2)  
    
    frame = ttk.Frame(win, padding=(12, 0)); frame.pack(fill=BOTH, expand=True, padx=12)

    s = ttk.Style()
    s.configure("Summary.Treeview.Heading", background="#2c3e6b", foreground="white",
                font=("Tahoma", 10, "bold"), relief="flat")
    s.map("Summary.Treeview.Heading", background=[("active", "#2c3e6b")])
    s.configure("Summary.Treeview", rowheight=28)

    tree = ttk.Treeview(frame, columns=("Description","Count"), show="headings",
                        height=14, style="Summary.Treeview")
    tree.heading("Description", text="Description")
    tree.heading("Count",       text="Count")
    tree.column("Description",  width=340, anchor=W,      stretch=True, minwidth=200)
    tree.column("Count",        width=120, anchor=CENTER, stretch=True, minwidth=80)
    tree.pack(fill=BOTH, expand=True)

    # Row colour tags
    tree.tag_configure("total",   background="#eaf0fb", foreground="#1a1a2e")
    tree.tag_configure("waiting", background="#fff3cd", foreground="#7d4e00")
    tree.tag_configure("served",  background="#d4edda", foreground="#155724")
    tree.tag_configure("emerg",   background="#fad4d4", foreground="#6b1a1a")
    tree.tag_configure("preg",    background="#d6eaf8", foreground="#1a3a5c")
    tree.tag_configure("normal",  background="#f0f0f0", foreground="#333333")
    tree.tag_configure("next",    background="#c8f0d4", foreground="#1a4731")
    tree.tag_configure("avg",     background="#fef9e7", foreground="#5d4037")

    tree.insert("", END, values=("Total Registered Today",     len(patients)+len(served)), tags=("total",))
    tree.insert("", END, values=("Currently Waiting",          len(patients)),             tags=("waiting",))
    tree.insert("", END, values=("Already Served",             len(served)),               tags=("served",))
    tree.insert("", END, values=("Average Waiting Proportion", avg_w),                     tags=("avg",))   
    tree.insert("", END, values=("", ""))
    tree.insert("", END, values=("Emergency in Queue",         counts["Emergency"]),       tags=("emerg",))
    tree.insert("", END, values=("Pregnant in Queue",          counts["Pregnant"]),        tags=("preg",))
    tree.insert("", END, values=("Normal in Queue",            counts["Normal"]),          tags=("normal",))
    tree.insert("", END, values=("", ""))
    tree.insert("", END, values=("Total Emergencies Served",   scounts["Emergency"]),      tags=("emerg",))  
    tree.insert("", END, values=("Total Pregnant Served",      scounts["Pregnant"]),       tags=("preg",)) 
    tree.insert("", END, values=("Total Normal Served",        scounts["Normal"]),         tags=("normal",)) 
    
    if patients:
        n = patients[0]
        tree.insert("", END, values=("", ""))
        tree.insert("", END,
                    values=(f"Next Patient:  {n['name']}  |  {n['category']}", ""),
                    tags=("next",))

    btn = ttk.Frame(win); btn.pack(pady=10)
    ttk.Button(btn, text="Export CSV", command=export_csv,     
               bootstyle="success-outline",  width=14).pack(side=LEFT, padx=6)
    ttk.Button(btn, text="Close",      command=win.destroy,
               bootstyle="secondary-outline", width=10).pack(side=LEFT, padx=6)

# Main Window

def main_window(root, username, role):  # Added - reuses the single root window
    root.title("MediCare SDG 3 Patient Queue System")
    root.resizable(True, True)
    try:    root.state("zoomed")
    except: root.attributes("-zoomed", True)
    root.minsize(900, 600)
    root.maxsize(1920, 1080)
    
    hdr = ttk.Frame(root, bootstyle="primary", padding=(14, 8))
    hdr.pack(fill=X)
    ttk.Label(hdr, text="MediCare Community Clinic - Sierra Leone",
              font=("Tahoma", 12, "bold"),
              bootstyle="inverse-primary").pack(side=LEFT)
    ttk.Label(hdr, text=f"  {role}: {username}", 
              font=("Tahoma", 10),
              bootstyle="inverse-primary").pack(side=LEFT, padx=16)
    clk = ttk.Label(hdr, text="", font=("Tahoma", 10),
                    bootstyle="inverse-primary")
    clk.pack(side=RIGHT)

    def tick():
        if not root.winfo_exists():
            return
        clk.config(text=datetime.now().strftime("%H:%M:%S"))
        root.after(1000, tick)
    tick()

    # Stats bar
    stats_frame = ttk.Frame(root, padding=(14, 6))
    stats_frame.pack(fill=X)
    waiting_lbl = ttk.Label(stats_frame, text="Waiting: 0",
                            font=("Tahoma", 10, "bold"), bootstyle="warning")
    waiting_lbl.pack(side=LEFT, padx=(0, 20))
    served_lbl = ttk.Label(stats_frame, text="Served: 0",
                           font=("Tahoma", 10, "bold"), bootstyle="success")
    served_lbl.pack(side=LEFT)

    def update_stats():
        waiting_lbl.config(text=f"Waiting: {len(patients)}")
        served_lbl.config(text=f"Served: {len(served)}")

    ttk.Separator(root).pack(fill=X)

    # Menu buttons
    menu = ttk.Frame(root, padding=20)
    menu.pack(fill=BOTH, expand=True)

    ttk.Label(menu, text="Patient Queue Management",
              font=("Tahoma", 15, "bold"),
              bootstyle="primary").pack(pady=(0, 6))
    ttk.Label(menu, text="Use the options below to manage the clinic queue",
              font=("Tahoma", 10),
              bootstyle="secondary").pack(pady=(0, 14))

    def open_register():
        open_register_dashboard(root, update_stats)

    buttons = [
        ("Register Patient",  "success",          open_register),
        ("View Queue",        "primary",          lambda: open_queue_dashboard(root)),
        ("Search Patient",    "info",             lambda: open_search_dashboard(root)),
        ("Edit / Delete",     "warning-outline",   lambda: open_edit_dashboard(root)),   # Added
        ("Served Patients",   "success-outline",  lambda: open_served_dashboard(root)),
        ("Summary",           "secondary-outline",lambda: open_summary_dashboard(root)),
    ]

    for label, style, cmd in buttons:
        ttk.Button(menu, text=label, command=cmd,
                   bootstyle=style, width=28).pack(pady=5)

    ttk.Separator(root).pack(fill=X)

    foot = ttk.Frame(root, padding=(10, 6)); foot.pack(fill=X)

    def on_exit():
        if messagebox.askyesno("Exit", "Exit MediQueue?"):
            auto_backup()   # ADDED: save dated backup CSV on close
            root.destroy()

    ttk.Button(foot, text="Exit", command=on_exit,
               bootstyle="danger-outline", width=12).pack(side=RIGHT, padx=10)

    update_stats()
    
    # Entry Point
if __name__ == "__main__":
    root = ttk.Window(themename="flatly")  # single Tk root for the whole app
    show_login_screen(root, main_window)
    root.mainloop()