""" Patient Queue Management System - MediCare Community Clinic, Sierra Leone
GUI: ttkbootstrap (flatly theme)
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime

# IN-MEMORY DATA
patients = []   # list of patient dicts
served   = []   # list of served patient dicts
counter  = [1]  # patient ID counter

PRIORITY = {"Emergency": 1, "Pregnant": 2, "Normal": 3}

# CORE FUNCTIONS

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

#  VALIDATION

def ok_name(t):  return bool(t.strip()) and t.replace(" ", "").isalpha()
def ok_age(t):   return t.isdigit() and 0 <= int(t) <= 120
def ok_note(t):  return bool(t.strip()) and not t.strip().isdigit()
def ok_time(t):
    return (len(t) == 5 and t[2] == ":" and t[:2].isdigit() and t[3:].isdigit()
            and 0 <= int(t[:2]) <= 23 and 0 <= int(t[3:]) <= 59)

# DASHBOARDS

def open_queue_dashboard(parent):
    win = ttk.Toplevel(parent)
    win.title("Live Queue")
    win.geometry("1100x650")

    ttk.Label(win, text="Waiting Queue", font=("Helvetica", 13, "bold"),
              bootstyle="primary").pack(pady=(10, 2))
    ttk.Separator(win).pack(fill=X, padx=10)

    cols   = ("#", "ID", "Name", "Age", "Category", "Arrived", "Complaint")
    widths = [60,  90,   160,    60,    110,        90,        170]

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
    s.configure("Queue.Treeview.Heading", background="#1a4f8a", foreground="white", font=("Helvetica", 10, "bold"), relief="flat")
    s.map("Queue.Treeview.Heading", background=[("active","#1a4f8a")])
    tree.configure(style="Queue.Treeview")
    tree.tag_configure("next",  background="#c8f0d4", foreground="#1a4731")
    tree.tag_configure("emerg", background="#fad4d4", foreground="#6b1a1a")
    tree.tag_configure("preg",  background="#d6eaf8", foreground="#1a3a5c")

    ttk.Label(win, text="Green = Next   Red = Emergency   Blue = Pregnant",
              font=("Helvetica", 9), bootstyle="secondary").pack(anchor=W, padx=12)

    def refresh():
        tree.delete(*tree.get_children())
        if not patients:
            tree.insert("", END, values=("-", "-", "No patients waiting", "-", "-", "-", " -"))
            return
        for i, p in enumerate(patients, 1):
            tag = ("next" if i == 1 else
                   "emerg" if p["category"] == "Emergency" else
                   "preg"  if p["category"] == "Pregnant"  else "")
            tree.insert("", END, values=(i, p["id"], p["name"], p["age"],
                        p["category"], p["arrived"], p["complaint"]), tags=(tag,))

    def call_next():
        if not patients:
            messagebox.showinfo("Empty", "No patients in queue."); return
        p = patients[0]
        if not messagebox.askyesno("Call Next",
            f"Call: {p['name']}  ({p['category']})\nComplaint: {p['complaint']}"): return
        called = call_next_patient()
        nxt = f"Next: {patients[0]['name']} ({patients[0]['category']})" if patients else "Queue is now empty."
        messagebox.showinfo("Now Calling",
            f"{called['name'].upper()} — Ticket #{called['queue_no']}\n"
            f"Category : {called['category']}\nComplaint: {called['complaint']}\n\n{nxt}")
        refresh()

    btn = ttk.Frame(win); btn.pack(pady=8)
    ttk.Button(btn, text="Call Next", command=call_next,
               bootstyle="success", width=16).pack(side=LEFT, padx=6)
    ttk.Button(btn, text="Refresh",  command=refresh,
               bootstyle="info-outline", width=14).pack(side=LEFT, padx=6)
    ttk.Button(btn, text="Close",        command=win.destroy,
               bootstyle="secondary-outline", width=10).pack(side=LEFT, padx=6)
    refresh()


def open_register_dashboard(parent, on_done):
    win = ttk.Toplevel(parent)
    win.title("Register Patient")
    win.geometry("480x440")
    win.grab_set()

    ttk.Label(win, text="Register New Patient",
              font=("Helvetica", 12, "bold")).pack(pady=10)
    ttk.Separator(win).pack(fill=X, padx=10)

    frm = ttk.Frame(win, padding=16); frm.pack(fill=BOTH, expand=True)

    nv = tk.StringVar(); av = tk.StringVar()
    cv = tk.StringVar(); tv = tk.StringVar(value=datetime.now().strftime("%H:%M"))
    kv = tk.StringVar(value="Normal")

    for i, (lbl, var) in enumerate([("Full Name", nv), ("Age", av),
                                     ("Complaint", cv), ("Arrived (HH:MM)", tv)]):
        ttk.Label(frm, text=f"{lbl}:").grid(row=i, column=0, sticky=W, pady=6)
        ttk.Entry(frm, textvariable=var, width=28).grid(row=i, column=1, pady=6, padx=(8, 0))

    ttk.Label(frm, text="Category:").grid(row=4, column=0, sticky=W, pady=6)
    ttk.Combobox(frm, textvariable=kv, width=26, state="readonly",
                 values=["Emergency", "Pregnant", "Normal"]).grid(
                 row=4, column=1, pady=6, padx=(8, 0))

    err = ttk.Label(frm, text="", bootstyle="danger", font=("Helvetica", 9))
    err.grid(row=5, column=0, columnspan=2, pady=2)

    def submit():
        n, a, c, t, k = (nv.get().strip(), av.get().strip(),
                         cv.get().strip(), tv.get().strip(), kv.get())
        for ok, msg in [(ok_name(n), "!!! Name: letters only"),
                        (ok_age(a),  "!!! Age: 0-120"),
                        (ok_note(c), "!!! Enter a complaint"),
                        (ok_time(t), "!!! Time must be HH:MM")]:
            if not ok: err.config(text=msg); return

        pid = register_patient(n, int(a), c, t, k)
        pos = next((i+1 for i, p in enumerate(patients) if p["id"] == pid), "?")
        messagebox.showinfo("Registered",
            f"Name     : {n.title()}\nID       : {pid}\n"
            f"Category : {k}\nPosition : {pos} of {len(patients)}")
        on_done()
        win.destroy()

    ttk.Button(frm, text="Register Patient", command=submit,
               bootstyle="success", width=18).grid(row=6, column=0, columnspan=2, pady=10)


def open_search_dashboard(parent):
    win = ttk.Toplevel(parent)
    win.title("Search Patient")
    win.geometry("1100x620")

    ttk.Label(win, text="Search Patient", font=("Helvetica", 13, "bold"),
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
                 font=("Helvetica", 10, "bold"), relief="flat")
    s2.map("Search.Treeview.Heading", background=[("active", "#0d6eaa")])
    s2.configure("Search.Treeview", rowheight=26)
    tree   = ttk.Treeview(frame, columns=cols, show="headings", height=12, style="Search.Treeview")
    for c, w in zip(cols, widths):
        tree.heading(c, text=c); tree.column(c, width=w, anchor=CENTER, minwidth=60, stretch=True)
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
        info.config(text=f"{len(res)} result(s) found." if res else f"No match for '{term}'.")

    sv.trace_add("write", do_search)
    ttk.Button(win, text="Close", command=win.destroy,
               bootstyle="secondary-outline", width=10).pack(pady=6)


def open_served_dashboard(parent):
    win = ttk.Toplevel(parent)
    win.title("Served Patients")
    win.geometry("1100x620")

    ttk.Label(win, text=f"Served Today — {len(served)} patient(s)",
              font=("Helvetica", 13, "bold"), bootstyle="success").pack(pady=(10, 2))
    ttk.Separator(win).pack(fill=X, padx=10, pady=(0, 8))

    cols   = ("ID", "Name", "Age", "Category", "Arrived", "Complaint")
    widths = [90,   150,    60,    110,        90,        200]
    frame  = ttk.Frame(win); frame.pack(fill=BOTH, expand=True, padx=10)

    s3 = ttk.Style()
    s3.configure("Served.Treeview.Heading", background="#198754", foreground="white",
                 font=("Helvetica", 10, "bold"), relief="flat")
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

    if not served:
        tree.insert("", END, values=("—", "No patients served yet", "—", "—", "—", "—"))
    else:
        for i, p in enumerate(served):
            tag = "odd" if i % 2 == 0 else "even"
            tree.insert("", END, values=(p["id"], p["name"], p["age"],
                        p["category"], p["arrived"], p["complaint"]), tags=(tag,))

    ttk.Button(win, text="Close", command=win.destroy,
               bootstyle="secondary-outline", width=10).pack(pady=10)


def open_summary_dashboard(parent):
    win = ttk.Toplevel(parent)
    win.title("Summary")
    win.geometry("560x480")

    ttk.Label(win, text="Today's Summary", font=("Helvetica", 13, "bold"),
              bootstyle="primary").pack(pady=(10, 2))
    ttk.Separator(win).pack(fill=X, padx=10, pady=(0, 10))

    counts = queue_summary()

    # Summary table 
    frame = ttk.Frame(win, padding=(12, 0)); frame.pack(fill=BOTH, expand=True, padx=12)

    s = ttk.Style()
    s.configure("Summary.Treeview.Heading", background="#2c3e6b", foreground="white",
                font=("Helvetica", 10, "bold"), relief="flat")
    s.map("Summary.Treeview.Heading", background=[("active", "#2c3e6b")])
    s.configure("Summary.Treeview", rowheight=30)

    cols   = ("Description", "Count")
    tree   = ttk.Treeview(frame, columns=cols, show="headings",
                          height=10, style="Summary.Treeview")
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

    # Insert rows
    tree.insert("", END, values=("Total Registered Today", len(patients) + len(served)), tags=("total",))
    tree.insert("", END, values=("Currently Waiting",      len(patients)),               tags=("waiting",))
    tree.insert("", END, values=("Already Served",         len(served)),                 tags=("served",))
    tree.insert("", END, values=("",                       ""),                          tags=())
    tree.insert("", END, values=("Emergency in Queue",     counts["Emergency"]),         tags=("emerg",))
    tree.insert("", END, values=("Pregnant in Queue",      counts["Pregnant"]),          tags=("preg",))
    tree.insert("", END, values=("Normal in Queue",        counts["Normal"]),            tags=("normal",))

    if patients:
        n = patients[0]
        tree.insert("", END, values=("", ""), tags=())
        tree.insert("", END,
                    values=(f"Next Patient:  {n['name']}  |  {n['category']}", ""),
                    tags=("next",))

    ttk.Button(win, text="Close", command=win.destroy,
               bootstyle="secondary-outline", width=10).pack(pady=12)

# MAIN WINDOW

def main():
    root = ttk.Window(themename="flatly")
    root.title("MediCare Community Clinic - Sierra Leone")
    try:
        root.state("zoomed")
    except:
        root.attributes("-zoomed", True)
    root.minsize(900, 600)
    root.maxsize(1920, 1080)

    # Header
    hdr = ttk.Frame(root, bootstyle="primary", padding=(14, 8))
    hdr.pack(fill=X)
    ttk.Label(hdr, text="MediCare Community Clinic - Sierra Leone",
              font=("Helvetica", 12, "bold"),
              bootstyle="inverse-primary").pack(side=LEFT)
    clk = ttk.Label(hdr, text="", font=("Helvetica", 10),
                    bootstyle="inverse-primary")
    clk.pack(side=RIGHT)

    def tick():
        clk.config(text=datetime.now().strftime("%H:%M:%S"))
        root.after(1000, tick)
    tick()

    # Stats bar
    stats_frame = ttk.Frame(root, padding=(14, 6))
    stats_frame.pack(fill=X)
    waiting_lbl = ttk.Label(stats_frame, text="Waiting: 0",
                            font=("Helvetica", 10, "bold"), bootstyle="warning")
    waiting_lbl.pack(side=LEFT, padx=(0, 20))
    served_lbl = ttk.Label(stats_frame, text="Served: 0",
                           font=("Helvetica", 10, "bold"), bootstyle="success")
    served_lbl.pack(side=LEFT)

    def update_stats():
        waiting_lbl.config(text=f"Waiting: {len(patients)}")
        served_lbl.config(text=f"Served: {len(served)}")

    ttk.Separator(root).pack(fill=X)

    # Menu buttons
    menu = ttk.Frame(root, padding=20)
    menu.pack(fill=BOTH, expand=True)

    ttk.Label(menu, text="Patient Queue Management",
              font=("Helvetica", 15, "bold"),
              bootstyle="primary").pack(pady=(0, 6))
    ttk.Label(menu, text="Use the options below to manage the clinic queue",
              font=("Helvetica", 10),
              bootstyle="secondary").pack(pady=(0, 14))

    def open_register():
        open_register_dashboard(root, update_stats)

    buttons = [
        ("Register Patient",  "success",          open_register),
        ("View Queue",        "primary",          lambda: open_queue_dashboard(root)),
        ("Search Patient",    "info",             lambda: open_search_dashboard(root)),
        ("Served Patients",   "success-outline",  lambda: open_served_dashboard(root)),
        ("Summary",           "secondary-outline",lambda: open_summary_dashboard(root)),
    ]

    for label, style, cmd in buttons:
        ttk.Button(menu, text=label, command=cmd,
                   bootstyle=style, width=28).pack(pady=5)

    ttk.Separator(root).pack(fill=X)
    ttk.Button(root, text="Exit",
               command=lambda: root.destroy() if messagebox.askyesno("Exit", "Exit MediQueue?") else None,
               bootstyle="danger-outline", width=14).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()