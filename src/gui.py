"""GUI: ttkbootstrap (flatly theme)"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Import all the functions and data structure from logic
from logic import *
from utils import *

       # Login Screen 
def show_login_screen(root, on_success):
    load_staff_accounts()  
    load_activity_log()     
    load_appointments()     
    load_announcements()
    load_session() #  Added for exporting file after exisiting the program    

    root.title("MediQueue - Staff Login")
    root.geometry("600x640")
    root.resizable(False, False)
    try: root.state("normal")
    except: pass

    win = ttk.Frame(root)
    win.pack(fill=BOTH, expand=True)

    ttk.Label(win, text="Welcome to MediCare",
                            font=("Tahoma", 17, "bold"), 
                            bootstyle="primary").pack(pady=(36, 2))
    
    # Patient Queue
    ttk.Label(win, text="Patient Queue System",
                           font=("Tahoma", 14), 
                           bootstyle="primary").pack()
    
    # Receptionist & Nurse 
    ttk.Label(win, text="Receptionist & Nurse Staff Login",
                           font=("Tahoma", 11), 
                           bootstyle="secondary").pack(pady=(6, 18))
    
    ttk.Separator(win).pack(fill=X, 
                            padx=40, pady=(0, 20))

    frm = ttk.Frame(win, padding=(40, 0)); frm.pack()

    uv = tk.StringVar(); pv = tk.StringVar()
    rv = tk.StringVar(value="Receptionist")

    for i, (lbl, var, show) in enumerate([("Username", uv, ""), ("Password", pv, "*")]):
        ttk.Label(frm, text=f"{lbl}:", font=("Tahoma", 12)).grid(
                                                            row=i, 
                                                            column=0, 
                                                            sticky=W, 
                                                            pady=12)
        
        ttk.Entry(frm, textvariable=var, show=show, width=28,
                  font=("Tahoma", 12)).grid(row=i, 
                                            column=1, 
                                            pady=12, 
                                            padx=(12, 0))

    # Role Selection Dropdown
    ttk.Label(frm, text="Role:", font=("Tahoma", 12)).grid(row=2, 
                                                           column=0, sticky=W, pady=12)
    ttk.Combobox(frm, textvariable=rv, width=26, state="readonly",
                 values=["Receptionist", "Nurse"],
                 font=("Tahoma", 12)).grid(row=2, 
                                           column=1, 
                                           pady=12, 
                                           padx=(12, 0))

    err = ttk.Label(frm, text="", bootstyle="danger", font=("Tahoma", 10), wraplength=380)
    err.grid(row=3, column=0, columnspan=2, pady=8)

    # Validate User Login Credentials
    def do_login():
        u, p, r = uv.get().strip(), pv.get(), rv.get()
        if not u or not p:
            err.config(text="Please enter your username and password"); return

        # Lock account after 3 failed attempts
        attempts = login_attempts.get(u, 0)
        if attempts >= 3:
            err.config(text="Account locked. Too many failed attempts."); return

        if u not in staff_accounts:
            err.config(text="Username not found. Register first."); return

        if staff_accounts[u]["password_hash"] != hash_password(p):
            login_attempts[u] = attempts + 1
            remaining = 3 - login_attempts[u]
            err.config(text=f"Incorrect password. {remaining} attempt(s) left."); return

        if staff_accounts[u]["role"] != r:
            err.config(text=f"This account is registered as {staff_accounts[u]['role']}."); return

        login_attempts[u] = 0 
        current_user[0] = f"{u} ({r})"  
        log_activity(f"{u} ({r}) logged in") 
        win.destroy()
        on_success(root, u, r)

    # User Registration Function
    def do_register():
        u, p, r = uv.get().strip(), pv.get(), rv.get()
        if not u or not p:
            err.config(text="Enter a username and password to register."); return
        if len(p) < 4:
            err.config(text="Password must be at least 4 characters."); return
        if u in staff_accounts:
            err.config(text="Username already taken. Choose another."); return
        staff_accounts[u] = {"password_hash": hash_password(p), "role": r}
        save_staff_accounts()
        err.config(text=f"{r} '{u}' registered successfully. You can now log in.")

    # Login and Registration Buttons
    btn = ttk.Frame(frm)
    btn.grid(row=4, column=0, columnspan=2, pady=20)
    ttk.Button(btn, text="Login",    command=do_login,
               bootstyle="primary",         width=16).pack(side=LEFT, padx=10)
    ttk.Button(btn, text="Register", command=do_register,
               bootstyle="success-outline", width=16).pack(side=LEFT, padx=10)

# Create and Configure Treeview Widget
def make_tree(parent, cols, widths, heading_bg="#1a4f8a", 
              rowheight=26,
              height=14, wide_cols=("Name", "Complaint")):
    frame = ttk.Frame(parent); frame.pack(fill=BOTH, 
                                          expand=True, 
                                          padx=10, 
                                          pady=8)

    # Treeview Styling
    style_name = f"T{id(cols)}.Treeview"
    s = ttk.Style()
    s.configure(f"{style_name}.Heading", 
                               background=heading_bg, 
                               foreground="white",
                               font=("Tahoma", 11, "bold"), 
                               relief="flat")
    
    s.map(f"{style_name}.Heading", background=[("active", heading_bg)])
    s.configure(style_name, rowheight=rowheight)

    tree = ttk.Treeview(frame, 
                        columns=cols, 
                        show="headings", 
                        height=height, 
                        style=style_name)
    
    for c, w in zip(cols, widths):
        tree.heading(c, text=c)
        tree.column(c, width=w, 
                    anchor=CENTER, 
                    minwidth=50, 
                    stretch=True)
        
    for c in wide_cols:
        if c in cols:
            tree.column(c, anchor=W, stretch=True)

    sb = ttk.Scrollbar(frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side=LEFT, fill=BOTH, expand=True); sb.pack(side=LEFT, fill=Y)
    return tree

# Get Selected Patient ID from Treeview
def get_selected_id(tree, col_index=0):
    sel = tree.selection()
    if not sel:
        return None
    pid = tree.item(sel[0], "values")[col_index]
    return None if pid in ("-",) else pid

# Edit / Delete Dashboard
def open_edit_dashboard(parent, update_stats_cb=None): 
    win = ttk.Toplevel(parent)
    win.title("Edit / Delete Patient")
    win.geometry("500x600")
    win.grab_set()

    ttk.Label(win, text="Edit or Delete Patient Record",
              font=("Tahoma", 13, "bold")).pack(pady=10)
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

    for i, (lbl, var) in enumerate([("Full Name", nv), 
                                     ("Age", av),
                                     ("Contact", ctv), 
                                     ("Complaint", cv),
                                     ("Arrived (HH:MM)", tv)]):
        
        ttk.Label(frm, text=f"{lbl}:").grid(row=i, column=0, sticky=W, pady=5)
        ttk.Entry(frm, textvariable=var, width=28).grid(row=i, 
                                                        column=1, 
                                                        pady=5, 
                                                        padx=(8, 0))

    ttk.Label(frm, text="Gender:").grid(row=5, column=0, sticky=W, pady=5)
    ttk.Combobox(frm, textvariable=gv, width=26, 
                 state="readonly",
                 values=["Male", "Female"]).grid(row=5, 
                                                 column=1, 
                                                 pady=5, 
                                                 padx=(8, 0))

    ttk.Label(frm, text="Category:").grid(row=6, column=0, sticky=W, pady=5)
    ttk.Combobox(frm, textvariable=kv, 
                 width=26, 
                 state="readonly",
                 values=["Emergency", "Pregnant", "Normal"]).grid(row=6, 
                                                                  column=1, 
                                                                  pady=5, 
                                                                  padx=(8, 0))

    err = ttk.Label(frm, text="", bootstyle="danger", font=("Tahoma", 9))
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
        n, a, ct, c, t, g, k = (nv.get().strip(), 
                                av.get().strip(),
                                ctv.get().strip(), 
                                cv.get().strip(),
                                tv.get().strip(), 
                                gv.get(), kv.get())
        
        for ok, msg in [(ok_name(n),     "Name: letters only"),
                        (ok_age(a),      "Age: 0 to 120"),
                        (ok_contact(ct), "Contact: digits only, 7-15 numbers"),
                        (ok_note(c),     "Enter a valid complaint"),
                        (ok_time(t),     "Time must be HH:MM")]:
            if not ok: err.config(text=msg); return
        if g == "Male" and k == "Pregnant":
            err.config(text="Male cannot be categorised as Pregnant"); return
        update_patient(found[0]["id"], n, int(a), g, ct, c, t, k)
        messagebox.showinfo("Updated", f"Patient {found[0]['id']} updated")
        if update_stats_cb: update_stats_cb()
        win.destroy()

    def do_delete():
        if not found[0]: err.config(text="Search for a patient first"); return
        pid  = found[0]["id"]
        name = found[0]["name"]
        if not messagebox.askyesno("Confirm Delete",
            f"Delete {pid} - {name}?\nThis cannot be undone"):
            return

        reason_win = ttk.Toplevel(win)
        reason_win.title("Cancellation Reason")
        reason_win.geometry("380x220")
        reason_win.grab_set()

        ttk.Label(reason_win, text=f"Reason for deleting {pid}:",
                  font=("Tahoma", 11, "bold")).pack(pady=(14, 6))
        reason_var = tk.StringVar(value="Patient request")
        ttk.Combobox(reason_win, 
                    textvariable=reason_var, 
                    width=30, 
                    state="readonly",
                    values=["Patient request", 
                             "Duplicate entry", 
                             "Wrong information",
                             "No longer needed", 
                             "Other"]).pack(pady=6)

        note_var = tk.StringVar()
        ttk.Label(reason_win, text="Additional note (optional):").pack(pady=(10, 2))
        ttk.Entry(reason_win, textvariable=note_var, width=34).pack()

        def confirm_delete():
            full_reason = reason_var.get()
            if note_var.get().strip():
                full_reason += f" - {note_var.get().strip()}"
            delete_patient(pid)
            record_cancellation(pid, name, full_reason)
            messagebox.showinfo("Deleted", f"Patient {pid} removed.\nReason: {full_reason}")
            if update_stats_cb: update_stats_cb()
            reason_win.destroy()
            win.destroy()

        ttk.Button(reason_win, text="Confirm Deletion", command=confirm_delete,
                   bootstyle="danger", width=18).pack(pady=14)

    ttk.Button(top, text="Search", command=do_search,
               bootstyle="info", width=10).pack(side=LEFT, padx=8)

    btn = ttk.Frame(win); btn.pack(pady=6)
    ttk.Button(btn, text="Update", command=do_update,
               bootstyle="primary",          width=14).pack(side=LEFT, padx=6)
    ttk.Button(btn, text="Delete", command=do_delete,
               bootstyle="danger-outline",   width=14).pack(side=LEFT, padx=6)
    ttk.Button(btn, text="Cancel", command=win.destroy,
               bootstyle="secondary-outline",width=10).pack(side=LEFT, padx=6)

# Queue Dashboard
def open_queue_dashboard(parent, update_stats_cb=None, role="Nurse"):
    win = ttk.Toplevel(parent)
    win.title("Live Queue")
    win.geometry("1100x680")

    ttk.Label(win, text="Waiting Queue", 
                               font=("Tahoma", 14, "bold"),
                               bootstyle="primary").pack(pady=(10, 2))
    ttk.Separator(win).pack(fill=X, padx=10)

    filter_bar = ttk.Frame(win, padding=(10, 6)); filter_bar.pack(fill=X)
    ttk.Label(filter_bar, text="Filter by Category:").pack(side=LEFT, padx=(0, 8))
    filter_var = tk.StringVar(value="All")
    ttk.Combobox(filter_bar, textvariable=filter_var, width=14, state="readonly",
                 values=["All", "Emergency", "Pregnant", "Normal"]).pack(side=LEFT)

    cols   = ("#", "ID", "Name", "Age", "Category", "Arrived", "Complaint", "Est. Wait", "Nurse")
    widths = [50,   70,   150,    50,    100,        80,        160,          90,        100]

    frame = ttk.Frame(win); frame.pack(fill=BOTH, expand=True, padx=10, pady=8)
    tree = ttk.Treeview(frame, 
                        columns=cols, 
                        show="headings", 
                        height=12)
    
    for c, w in zip(cols, widths):
        tree.heading(c, text=c)
        tree.column(c, width=w, anchor=CENTER, minwidth=50, stretch=True)
    tree.column("Name",      anchor=W, stretch=True)
    tree.column("Complaint", anchor=W, stretch=True)
    sb = ttk.Scrollbar(frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side=LEFT, fill=BOTH, expand=True); sb.pack(side=LEFT, fill=Y)

    s = ttk.Style()
    s.configure("Queue.Treeview.Heading", background="#1a4f8a", foreground="white",
                                                                  font=("Tahoma", 11, "bold"), 
                                                                  relief="flat")
    s.map("Queue.Treeview.Heading", background=[("active", "#1a4f8a")])
    tree.configure(style="Queue.Treeview")
    tree.tag_configure("next",  background="#c8f0d4", foreground="#1a4731")
    tree.tag_configure("emerg", background="#fad4d4", foreground="#6b1a1a")
    tree.tag_configure("preg",  background="#d6eaf8", foreground="#1a3a5c")

    ttk.Label(win, text="Green = Next   Red = Emergency   Blue = Pregnant",
                                                              font=("Tahoma", 10), 
                                                              bootstyle="secondary").pack(anchor=W, padx=12)
   
    alert_lbl = ttk.Label(win, text="", font=("Tahoma", 9, "bold"), bootstyle="danger")
    alert_lbl.pack(anchor=W, padx=12, pady=(2, 0))

    def refresh():
        tree.delete(*tree.get_children())
        cat_f = filter_var.get()
        visible = [p for p in patients if cat_f == "All" or p["category"] == cat_f]

        if not patients:
            tree.insert("", END, values=("-", "-", "No patients waiting",
                                         "-", "-", "-", "-", "-", "-"))
            alert_lbl.config(text="")
        elif not visible:
            tree.insert("", END, values=("-", "-", f"No {cat_f} patients waiting",
                                         "-", "-", "-", "-", "-", "-"))
        else:
            for p in visible:
                i = patients.index(p) + 1
                tag = ("next"  if i == 1 else
                       "emerg" if p["category"] == "Emergency" else
                       "preg"  if p["category"] == "Pregnant"  else "")
                
                wait  = f"{i * AVG_MIN} min"
                nurse = p.get("assigned_nurse", "-")
                tree.insert("", END, values=(i, p["id"], p["name"], p["age"],
                            p["category"], p["arrived"], p["complaint"], wait, nurse),
                            tags=(tag,))
            overdue = get_overdue_patients()

            if overdue:
                names = ", ".join(p["name"] for p in overdue)
                alert_lbl.config(text=f"WARNING: {len(overdue)} patient(s) waiting over "
                                       f"{WAIT_ALERT_MIN} min - {names}")
            else:
                alert_lbl.config(text="")
        if win.winfo_exists():
            win.after(10000, refresh)

    filter_var.trace_add("write", lambda *_: refresh()) 

    def call_next():
        if not patients:
            messagebox.showinfo("Empty", "No patients in queue."); return
        p = patients[0]
        if not messagebox.askyesno("Call Next",
            f"Call: {p['name']}  ({p['category']})\nComplaint: {p['complaint']}"): return
        called = call_next_patient()
        if called is None:
            messagebox.showwarning("Queue Empty", "No patient available to call"); return
        log_activity(f"{current_user[0]} called {called['id']} ({called['name']})")
        nxt = (f"Next: {patients[0]['name']} ({patients[0]['category']})"
               
               if patients else "Queue is now empty")
        messagebox.showinfo("Now Calling",
            f"{called['name'].upper()} - Ticket #{called['queue_no']}\n"
            f"Category : {called['category']}\nComplaint: {called['complaint']}\n\n{nxt}")
        
        if update_stats_cb: update_stats_cb()
        refresh()

    def undo_call():
        if undo_last_call():
            messagebox.showinfo("Restored", "Last called patient returned to queue")
            if update_stats_cb: update_stats_cb()
            refresh()
        else:
            messagebox.showwarning("Nothing to Undo", "No recent call to restore")

    def open_assign_nurse():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Select a patient row first"); return
        values = tree.item(sel[0], "values")
        pid = values[1]
        if pid in ("-",):
            messagebox.showinfo("No Selection", "Select a patient row first"); return

        dlg = ttk.Toplevel(win)
        dlg.title("Assign Nurse")
        dlg.geometry("340x180")
        dlg.grab_set()
        ttk.Label(dlg, text=f"Assign nurse to {pid}", font=("Tahoma", 12, "bold")).pack(pady=12)
        nv = tk.StringVar()
        ttk.Entry(dlg, textvariable=nv, width=24).pack(pady=6)

        def confirm():
            name = nv.get().strip()
            if not name:
                return
            assign_nurse(pid, name)
            dlg.destroy()
            refresh()

        ttk.Button(dlg, text="Assign", command=confirm,
                   bootstyle="primary", width=14).pack(pady=10)

    def do_mark_absent():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Select a patient row first."); return
        values = tree.item(sel[0], "values")
        pid = values[1]
        if pid in ("-",):
            messagebox.showinfo("No Selection", "Select a patient row first."); return
        if messagebox.askyesno("Mark Absent", f"Mark {pid} as absent?"):
            mark_absent(pid)
            if update_stats_cb: update_stats_cb()
            refresh()

    btn = ttk.Frame(win); btn.pack(pady=8)

    if role == "Nurse":
        ttk.Button(btn, text="Call Next",     command=call_next,
                   bootstyle="success",          width=12).pack(side=LEFT, padx=3)
        ttk.Button(btn, text="Undo Call",     command=undo_call,
                   bootstyle="warning-outline",  width=12).pack(side=LEFT, padx=3)

    ttk.Button(btn, text="Mark Absent",   command=do_mark_absent,
               bootstyle="danger-outline",   width=12).pack(side=LEFT, padx=3)
    ttk.Button(btn, text="Assign Nurse",  command=open_assign_nurse,
               bootstyle="info-outline",     width=13).pack(side=LEFT, padx=3)
    ttk.Button(btn, text="Refresh",       command=refresh,
               bootstyle="info-outline",     width=10).pack(side=LEFT, padx=3)
    ttk.Button(btn, text="Close",         command=win.destroy,
               bootstyle="secondary-outline",width=9).pack(side=LEFT, padx=3)
    refresh()

# Register Dashboard
def open_register_dashboard(parent, on_done):
    win = ttk.Toplevel(parent)
    win.title("Register Patient")
    win.geometry("480x540")
    win.grab_set()

    ttk.Label(win, text="Register New Patient",
                                        font=("Tahoma", 13, "bold")).pack(pady=10)
    ttk.Separator(win).pack(fill=X, padx=10)

    frm = ttk.Frame(win, padding=16); frm.pack(fill=BOTH, expand=True)

    nv  = tk.StringVar(); av  = tk.StringVar()
    gv  = tk.StringVar(value="Male")
    ctv = tk.StringVar(); cv  = tk.StringVar()
    tv  = tk.StringVar(value=datetime.now().strftime("%H:%M"))
    kv  = tk.StringVar(value="Normal")

    # Fields rows 0-4
    for i, (lbl, var) in enumerate([("Full Name",       nv),
                                     ("Age",             av),
                                     ("Contact Number",  ctv),
                                     ("Complaint",       cv),
                                     ("Arrived (HH:MM)", tv)]):
        
        ttk.Label(frm, text=f"{lbl}:").grid(row=i, column=0, sticky=W, pady=5)
        ttk.Entry(frm, textvariable=var, width=28).grid(row=i, column=1, pady=6, padx=(8, 0))

    # Gender row 5
    ttk.Label(frm, text="Gender:").grid(row=5, column=0, sticky=W, pady=5)
    gender_cb = ttk.Combobox(frm, textvariable=gv, 
                                  width=26, state="readonly",
                                  values=["Male", "Female"])
    gender_cb.grid(row=5, 
                   column=1, 
                   pady=5, 
                   padx=(8, 0))

    # Category row 6
    ttk.Label(frm, text="Category:").grid(row=6, column=0, sticky=W, pady=5)
    cat_cb = ttk.Combobox(frm, 
                          textvariable=kv, 
                          width=26, 
                          state="readonly",
                          values=["Emergency", "Pregnant", "Normal"])
    cat_cb.grid(row=6, 
                column=1, 
                pady=5, 
                padx=(8, 0))

    # Error label row 7
    err = ttk.Label(frm, text="", bootstyle="danger", font=("Tahoma", 10))
    err.grid(row=7, column=0, columnspan=2, pady=2)

    def on_gender_change(*_):
        if gv.get() == "Male":
            cat_cb.config(values=["Emergency", "Normal"])
            if kv.get() == "Pregnant": kv.set("Normal")
        else:
            cat_cb.config(values=["Emergency", "Pregnant", "Normal"])
    gv.trace_add("write", on_gender_change)

    def submit():
        n, a, ct, c, t, k = (nv.get().strip(),  
                             av.get().strip(),
                            ctv.get().strip(), 
                            cv.get().strip(),
                            tv.get().strip(),  kv.get())
        
        for ok, msg in [(ok_name(n),     "Name: letters only"),
                        (ok_age(a),      "Age: 0-120"),
                        (ok_contact(ct), "Contact: digits only, 7-15 numbers"),
                        (ok_complaint(c),"Complaint: at least 3 characters"),
                        (ok_time(t),     "Time must be HH:MM")]:
            if not ok: err.config(text=msg); return

        # Warn if same name and contact already exists in queue
        if check_duplicate(n, ct):
            if not messagebox.askyesno("Possible Duplicate",
                f"A patient named {n.title()} with this contact already exists.\n"
                f"Register anyway?"):
                return

        pid  = register_patient_full(n, int(a), gv.get(), ct, c, t, k)
        pos  = next((i+1 for i, p in enumerate(patients) if p["id"] == pid), "?")
        wait = pos * AVG_MIN if isinstance(pos, int) else "?"
        log_activity(f"{current_user[0]} registered {pid} ({n.title()})") 
        messagebox.showinfo("Registered",
            f"Name     : {n.title()}\nID       : {pid}\n"
            f"Category : {k}\nPosition : {pos} of {len(patients)}\n"
            f"Est. Wait: {wait} min")
        on_done(); win.destroy()

    ttk.Button(frm, text="Register Patient", command=submit,
               bootstyle="success", width=18).grid(row=8, 
                                                   column=0, 
                                                   columnspan=2, 
                                                   pady=10)

# Search Dashboard
def open_search_dashboard(parent):
    win = ttk.Toplevel(parent)
    win.title("Search Patient")
    win.geometry("1100x680")

    ttk.Label(win, text="Search Patient", font=("Tahoma", 14, "bold"),
              bootstyle="primary").pack(pady=(10, 2))
    ttk.Separator(win).pack(fill=X, padx=10, pady=(0, 8))

    filter_frame = ttk.Frame(win, padding=(10, 4))
    filter_frame.pack(fill=X)

    ttk.Label(filter_frame, text="Name or ID:").pack(side=LEFT, padx=(0, 6))
    sv = tk.StringVar()
    ttk.Entry(filter_frame, textvariable=sv, width=24).pack(side=LEFT)

    ttk.Label(filter_frame, text="  Category:").pack(side=LEFT, padx=(10, 4))
    fcat = tk.StringVar(value="All")
    ttk.Combobox(filter_frame, textvariable=fcat, width=12, state="readonly",
                 values=["All", "Emergency", "Pregnant", "Normal"]).pack(side=LEFT)

    ttk.Label(filter_frame, text="  Status:").pack(side=LEFT, padx=(10, 4))
    fstat = tk.StringVar(value="All")
    ttk.Combobox(filter_frame, textvariable=fstat, width=10, state="readonly",
                 values=["All", "Waiting", "Served"]).pack(side=LEFT)

    cols   = ("ID", "Name", "Age", "Category", "Arrived", "Complaint", "Status")
    widths = [90,   150,    60,    110,        90,        160,         80]
    frame  = ttk.Frame(win); frame.pack(fill=BOTH, expand=True, padx=10, pady=8)

    s2 = ttk.Style()
    s2.configure("Search.Treeview.Heading", 
                 background="#0d6eaa", 
                 foreground="white",
                 font=("Tahoma", 11, "bold"), 
                 relief="flat")
    
    s2.map("Search.Treeview.Heading", background=[("active", "#0d6eaa")])
    s2.configure("Search.Treeview", rowheight=26)
    tree = ttk.Treeview(frame, 
                        columns=cols, 
                        show="headings",
                        height=14, 
                        style="Search.Treeview")
    
    for c, w in zip(cols, widths):
        tree.heading(c, text=c)
        tree.column(c, width=w, anchor=CENTER, minwidth=60, stretch=True)
    tree.column("Name",      anchor=W, stretch=True)
    tree.column("Complaint", anchor=W, stretch=True)

    sb = ttk.Scrollbar(frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side=LEFT, fill=BOTH, expand=True); sb.pack(side=LEFT, fill=Y)

    info = ttk.Label(win, text="Type to search...", bootstyle="secondary")
    info.pack(anchor=W, padx=12, pady=4)

    def do_search(*_):
        term  = sv.get().strip().lower()
        cat_f = fcat.get()
        sta_f = fstat.get()
        tree.delete(*tree.get_children())

        all_p = [(p, "Waiting") for p in patients] + [(p, "Served") for p in served]
        res = []
        for p, status in all_p:
            if term and term not in p["id"].lower() and term not in p["name"].lower():
                continue
            if cat_f != "All" and p["category"] != cat_f:
                continue
            if sta_f != "All" and status != sta_f:
                continue
            res.append((p, status))

        for p, status in res:
            tree.insert("", 
                        END, 
                        values=(p["id"], 
                                p["name"], 
                                p["age"],
                        p["category"], 
                        p["arrived"], 
                        p["complaint"], 
                        status))
        info.config(text=f"{len(res)} result(s) found." if res else "No matches found.")

    sv.trace_add("write",  do_search)
    fcat.trace_add("write",  do_search)
    fstat.trace_add("write", do_search)

    ttk.Button(win, text="Close", 
                    command=win.destroy,
                    bootstyle="secondary-outline", width=10).pack(pady=6)

# Served Dashboard
def open_served_dashboard(parent, role="Nurse"):
    win = ttk.Toplevel(parent)
    win.title("Served Patients")
    win.geometry("1100x660")

    ttk.Label(win, text=f"Served Today - {len(served)} patient(s)",
              font=("Tahoma", 14, "bold"), bootstyle="success").pack(pady=(10, 2))
    ttk.Separator(win).pack(fill=X, padx=10, pady=(0, 8))

    cols   = ("ID", "Name", "Age", "Category", "Arrived", "Complaint")
    widths = [90,   150,    60,    110,        90,        200]
    frame  = ttk.Frame(win); frame.pack(fill=BOTH, expand=True, padx=10)

    s3 = ttk.Style()
    s3.configure("Served.Treeview.Heading", 
                 background="#198754", 
                 foreground="white",
                 font=("Tahoma", 10, "bold"), 
                 relief="flat")
    s3.map("Served.Treeview.Heading", background=[("active", "#198754")])
    s3.configure("Served.Treeview", rowheight=28)

    tree = ttk.Treeview(frame, 
                        columns=cols, 
                        show="headings",
                        height=14, 
                        style="Served.Treeview")
    
    for c, w in zip(cols, widths):
        tree.heading(c, text=c)
        tree.column(c, width=w, anchor=CENTER, minwidth=60, stretch=True)
    tree.column("Name",      anchor=W, stretch=True)
    tree.column("Complaint", anchor=W, stretch=True)

    tree.tag_configure("odd",  background="#f7fbf7", foreground="#1a1a1a")
    tree.tag_configure("even", background="#e8f5e9", foreground="#1a1a1a")

    sb = ttk.Scrollbar(frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side=LEFT, fill=BOTH, expand=True); sb.pack(side=LEFT, fill=Y)

    def load_served():
        tree.delete(*tree.get_children())
        if not served:
            tree.insert("", END, values=("—", "No patients served yet", "—", "—", "—", "—"))
            return
        for i, p in enumerate(served):
            tag = "odd" if i % 2 == 0 else "even"
            tree.insert("", END, values=(p["id"], 
                                         p["name"], 
                                         p["age"],
                        p["category"], 
                        p["arrived"], 
                        p["complaint"]), tags=(tag,))

    def clear_served():
        if not served:
            messagebox.showinfo("Empty", "No served patients to clear."); return
        if messagebox.askyesno("Confirm Clear",
            f"Clear all {len(served)} served records?\nThis cannot be undone"):
            served.clear()
            last_called[0] = None
            load_served()
            messagebox.showinfo("Cleared", "Served patients list cleared.")

    def open_import():
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Select Backup CSV",
            filetypes=[("CSV files", "*.csv")])
        if not path: return
        try:
            import_backup(path)
            messagebox.showinfo("Imported", f"Records loaded from {os.path.basename(path)}")
            load_served()
        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    load_served()

    def do_export_served_only():
        filename = export_served_csv()
        messagebox.showinfo("Exported", f"Served patients saved to {filename}")

    btn = ttk.Frame(win); btn.pack(pady=8)

    # Receptionist can view served patients but cannot clear them
    if role == "Nurse":
        ttk.Button(btn, text="Clear Served", command=clear_served,
                   bootstyle="danger-outline",       width=15).pack(side=LEFT, padx=4)

    ttk.Button(btn, text="Export CSV",       command=export_csv,
               bootstyle="success-outline",      width=13).pack(side=LEFT, padx=4)
    ttk.Button(btn, text="Export Served Only", command=do_export_served_only,
               bootstyle="success-outline",      width=17).pack(side=LEFT, padx=4)
    ttk.Button(btn, text="Import Backup",    command=open_import,
               bootstyle="info-outline",         width=14).pack(side=LEFT, padx=4)
    ttk.Button(btn, text="Close",            command=win.destroy,
               bootstyle="secondary-outline",    width=9).pack(side=LEFT, padx=4)

# Summary Dashboard
def open_summary_dashboard(parent):
    win = ttk.Toplevel(parent)
    win.title("Summary")
    win.geometry("600x620")

    ttk.Label(win, text="Today's Summary",
                   font=("Tahoma", 14, "bold"),
                   bootstyle="primary").pack(pady=(10, 2))
    ttk.Separator(win).pack(fill=X, padx=10, pady=(0, 10))

    counts  = queue_summary()
    scounts = served_summary()
    avg_w   = round(len(patients) / max(1, len(patients) + len(served)), 2)

    complaints    = [p["complaint"] for p in served]
    top_complaint = max(set(complaints), key=complaints.count) if complaints else "N/A"
    hours         = [p["arrived"][:2] for p in served if p.get("arrived")]
    peak_hour     = (max(set(hours), key=hours.count) + ":00") if hours else "N/A"

    frame = ttk.Frame(win, padding=(12, 0)); frame.pack(fill=BOTH, expand=True, padx=12)

    s = ttk.Style()
    s.configure("Summary.Treeview.Heading", 
                background="#2c3e6b", 
                foreground="white",
                font=("Tahoma", 11, "bold"), 
                relief="flat")
    s.map("Summary.Treeview.Heading", background=[("active", "#2c3e6b")])
    s.configure("Summary.Treeview", rowheight=28)

    tree = ttk.Treeview(frame, columns=("Description", "Count"), 
                               show="headings",
                               height=16, style="Summary.Treeview")
    tree.heading("Description", text="Description")
    tree.heading("Count",       text="Count")
    tree.column("Description",  width=340, anchor=W,      stretch=True, minwidth=200)
    tree.column("Count",        width=120, anchor=CENTER, stretch=True, minwidth=80)
    tree.pack(fill=BOTH, expand=True)

    tree.tag_configure("total",   background="#eaf0fb", foreground="#1a1a2e")
    tree.tag_configure("waiting", background="#fff3cd", foreground="#7d4e00")
    tree.tag_configure("served",  background="#d4edda", foreground="#155724")
    tree.tag_configure("emerg",   background="#fad4d4", foreground="#6b1a1a")
    tree.tag_configure("preg",    background="#d6eaf8", foreground="#1a3a5c")
    tree.tag_configure("normal",  background="#f0f0f0", foreground="#333333")
    tree.tag_configure("next",    background="#c8f0d4", foreground="#1a4731")
    tree.tag_configure("avg",     background="#fef9e7", foreground="#5d4037")
    tree.tag_configure("info",    background="#f5f5f5", foreground="#333333")

    tree.insert("", END, values=("Total Registered Today",     len(patients)+len(served)), tags=("total",))
    tree.insert("", END, values=("Currently Waiting",          len(patients)),             tags=("waiting",))
    tree.insert("", END, values=("Already Served",             len(served)),               tags=("served",))
    tree.insert("", END, values=("Average Waiting Proportion", avg_w),                     tags=("avg",))
    tree.insert("", END, values=("Peak Hour",                  peak_hour),                 tags=("info",))
    tree.insert("", END, values=("Most Common Complaint",      top_complaint),             tags=("info",))
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

    def do_export_report():
        filename = export_daily_report()
        messagebox.showinfo("Report Saved", f"Daily report saved as {filename}")

    btn = ttk.Frame(win); btn.pack(pady=10)
    ttk.Button(btn, text="Export CSV",    command=export_csv,
               bootstyle="success-outline",   width=13).pack(side=LEFT, padx=5)
    ttk.Button(btn, text="Daily Report",  command=do_export_report,
               bootstyle="info-outline",      width=13).pack(side=LEFT, padx=5)
    ttk.Button(btn, text="Close",         command=win.destroy,
               bootstyle="secondary-outline", width=9).pack(side=LEFT, padx=5)

#  Appointment Dashboard
def open_appointment_dashboard(parent):
    win = ttk.Toplevel(parent)
    win.title("Appointment Scheduling")
    win.geometry("760x560")

    ttk.Label(win, text="Book & View Appointments", font=("Tahoma", 14, "bold"),
              bootstyle="primary").pack(pady=(10, 2))
    ttk.Separator(win).pack(fill=X, padx=10, pady=(0, 8))

    frm = ttk.Frame(win, padding=12); frm.pack(fill=X)

    nv = tk.StringVar(); ctv = tk.StringVar()
    dv = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
    tv = tk.StringVar(value="09:00")
    notev = tk.StringVar()

    for i, (lbl, var) in enumerate([("Patient Name", nv), 
                                    ("Contact", ctv),
                                    ("Date (DD/MM/YYYY)", dv), 
                                    ("Time (HH:MM)", tv),
                                    ("Note", notev)]):
        
        ttk.Label(frm, text=f"{lbl}:").grid(row=i, column=0, sticky=W, pady=4)
        ttk.Entry(frm, textvariable=var, width=30).grid(row=i, 
                                                        column=1, 
                                                        pady=4, 
                                                        padx=(8, 0))

    err = ttk.Label(frm, text="", bootstyle="danger", font=("Tahoma", 10))
    err.grid(row=5, 
             column=0, 
             columnspan=2, 
             pady=4)

    cols = ("Name", "Contact", "Date", "Time", "Note", "Booked By")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=10)

    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=110, anchor=W, stretch=True)
    tree.pack(fill=BOTH, expand=True, padx=10, pady=8)

    def refresh_list():
        tree.delete(*tree.get_children())
        for a in appointments:
            tree.insert("", END, values=(a["name"], 
                                         a["contact"], 
                                         a["date"],
                        a["time"], a["note"], a["booked_by"]))

    def submit_appt():
        n, ct, d, t, note = nv.get().strip(), ctv.get().strip(), dv.get().strip(), tv.get().strip(), notev.get().strip()

        if not ok_name(n):
            err.config(text="Name: letters only"); return
        if not ok_contact(ct):
            err.config(text="Contact: digits only, 7-15 numbers"); return
        if not ok_time(t):
            err.config(text="Time must be HH:MM"); return
        book_appointment(n, ct, d, t, note, current_user[0] or "Unknown")
        messagebox.showinfo("Booked", f"Appointment booked for {n.title()} on {d} {t}")
        refresh_list()

    ttk.Button(frm, text="Book Appointment", 
                    command=submit_appt,
               bootstyle="success", 
               width=20).grid(row=6, 
                              column=0, 
                              columnspan=2, 
                              pady=8)

    refresh_list()
    ttk.Button(win, text="Close", command=win.destroy,
               bootstyle="secondary-outline", width=10).pack(pady=6)

# Activity Dashboard 
def open_activity_log_dashboard(parent):
    win = ttk.Toplevel(parent)
    win.title("Staff Activity Log")
    win.geometry("600x560")

    ttk.Label(win, text="Staff Activity Log", font=("Tahoma", 14, "bold"),
              bootstyle="primary").pack(pady=(10, 2))
    ttk.Separator(win).pack(fill=X, padx=10, pady=(0, 8))

    box = tk.Listbox(win, font=("Consolas", 10))
    box.pack(fill=BOTH, expand=True, padx=10, pady=8)

    if not activity_log:
        box.insert(END, "No activity recorded yet.")
    else:
        for entry in reversed(activity_log):
            box.insert(END, entry)

    ttk.Button(win, text="Close", command=win.destroy,
               bootstyle="secondary-outline", width=10).pack(pady=6)

# Visit History Dashboard
def open_visit_history_dashboard(parent):
    win = ttk.Toplevel(parent)
    win.title("Visit History")
    win.geometry("700x560")

    ttk.Label(win, text="Patient Visit History", font=("Tahoma", 14, "bold"),
              bootstyle="primary").pack(pady=(10, 2))
    ttk.Separator(win).pack(fill=X, 
                            padx=10, 
                            pady=(0, 8))

    visit_counts = {}
    for p in served:
        visit_counts[p["name"]] = visit_counts.get(p["name"], 0) + 1

    cols = ("Patient Name", "Total Visits")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=16)
    tree.heading("Patient Name",  text="Patient Name")
    tree.heading("Total Visits",  text="Total Visits")
    tree.column("Patient Name",  width=300, anchor=W,      stretch=True)
    tree.column("Total Visits",  width=120, anchor=CENTER, stretch=True)
    tree.pack(fill=BOTH, expand=True, padx=10, pady=8)

    if not visit_counts:
        tree.insert("", END, values=("No visit history yet", ""))
    else:
        for name, count in sorted(visit_counts.items(), key=lambda x: -x[1]):
            tree.insert("", END, values=(name, count))

    ttk.Button(win, text="Close", command=win.destroy,
               bootstyle="secondary-outline", width=10).pack(pady=6)

# Announcement Dashboard
def open_announcements_dashboard(parent, role):
    win = ttk.Toplevel(parent)
    win.title("Clinic Announcements")
    win.geometry("520x480")

    ttk.Label(win, text="Clinic Announcements", font=("Tahoma", 14, "bold"),
              bootstyle="primary").pack(pady=(10, 2))
    ttk.Separator(win).pack(fill=X, padx=10, pady=(0, 8))

    box = tk.Listbox(win, font=("Tahoma", 10))
    box.pack(fill=BOTH, expand=True, padx=10, pady=8)

    def refresh_list():
        box.delete(0, END)
        if not announcements:
            box.insert(END, "No announcements posted yet.")
        else:
            for a in announcements:
                box.insert(END, a)

    refresh_list()

    if role == "Receptionist":
        frm = ttk.Frame(win, padding=8); frm.pack(fill=X)
        nv = tk.StringVar()
        ttk.Entry(frm, textvariable=nv, width=40).pack(side=LEFT, padx=(0, 6))

        def add_announcement():
            text = nv.get().strip()
            if not text: return
            announcements.append(text)
            save_announcements() 
            nv.set("")
            refresh_list()

        ttk.Button(frm, text="Post", command=add_announcement,
                   bootstyle="success", width=10).pack(side=LEFT)

    ttk.Button(win, text="Close", command=win.destroy,
               bootstyle="secondary-outline", width=10).pack(pady=6)

# Search By Date
def open_search_by_date_dashboard(parent):
    win = ttk.Toplevel(parent)
    win.title("Search by Date")
    win.geometry("900x560")

    ttk.Label(win, text="Search Patients by Registration Date", font=("Tahoma", 14, "bold"),
              bootstyle="primary").pack(pady=(10, 2))
    ttk.Separator(win).pack(fill=X, padx=10, pady=(0, 8))

    bar = ttk.Frame(win, padding=8); bar.pack(fill=X)
    ttk.Label(bar, text="Date (DD/MM/YYYY):").pack(side=LEFT, padx=(0, 8))
    dv = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
    ttk.Entry(bar, textvariable=dv, width=16).pack(side=LEFT)

    cols   = ("ID", "Name", "Age", "Category", "Arrived", "Status")
    widths = [80,   160,    50,    100,        80,        90]
    tree = ttk.Treeview(win, columns=cols, show="headings", height=14)

    for c, w in zip(cols, widths):
        tree.heading(c, text=c)
        tree.column(c, width=w, anchor=CENTER, stretch=True)
    tree.column("Name", anchor=W, stretch=True)
    tree.pack(fill=BOTH, expand=True, padx=10, pady=8)

    info = ttk.Label(win, text="", bootstyle="secondary")
    info.pack(anchor=W, padx=12)

    def do_search():
        tree.delete(*tree.get_children())
        results = search_by_date(dv.get().strip())
        for p in results:
            status = "Waiting" if p in patients else "Served"
            tree.insert("", END, values=(p["id"], 
                                         p["name"], 
                                         p["age"],
                        p["category"], p["arrived"], status))
            
        info.config(text=f"{len(results)} record(s) found." if results
                    else "No records found for this date.")

    ttk.Button(bar, text="Search", command=do_search,
               bootstyle="info", width=10).pack(side=LEFT, padx=8)

    ttk.Button(win, text="Close", command=win.destroy,
               bootstyle="secondary-outline", width=10).pack(pady=6)

# Absent Patient Dashboard
def open_absent_dashboard(parent, update_stats_cb=None):
    win = ttk.Toplevel(parent)
    win.title("Absent / Missed Patients")
    win.geometry("900x560")

    ttk.Label(win, text="Patients Who Missed Their Turn", font=("Tahoma", 14, "bold"),
              bootstyle="danger").pack(pady=(10, 2))
    ttk.Separator(win).pack(fill=X, padx=10, pady=(0, 8))

    cols   = ("ID", "Name", "Age", "Category", "Arrived", "Complaint", "Status")
    widths = [80,   150,    50,    100,        80,        180,         80]

    s = ttk.Style()
    s.configure("Absent.Treeview.Heading", background="#a83232", foreground="white",
                font=("Tahoma", 11, "bold"), relief="flat")
    s.map("Absent.Treeview.Heading", background=[("active", "#a83232")])

    frame = ttk.Frame(win); frame.pack(fill=BOTH, expand=True, padx=10, pady=8)
    tree = ttk.Treeview(frame, columns=cols, show="headings",
                        height=14, style="Absent.Treeview")
    for c, w in zip(cols, widths):
        tree.heading(c, text=c)
        tree.column(c, width=w, anchor=CENTER, stretch=True)
    tree.column("Name",      anchor=W, stretch=True)
    tree.column("Complaint", anchor=W, stretch=True)
    sb = ttk.Scrollbar(frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side=LEFT, fill=BOTH, expand=True); sb.pack(side=LEFT, fill=Y)

    def refresh():
        tree.delete(*tree.get_children())
        if not absent:
            tree.insert("", END, values=("-", "No absent patients", "-", "-", "-", "-", "-"))
            return
        for p in absent:
            tree.insert("", END, values=(p["id"], 
                                         p["name"], 
                                         p["age"],
                        p["category"], 
                        p["arrived"], 
                        p["complaint"], "Absent"))

    def do_recall():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Select a patient row first."); return
        values = tree.item(sel[0], "values")
        pid = values[0]
        if pid == "-":
            messagebox.showinfo("No Selection", "Select a patient row first."); return
        if messagebox.askyesno("Recall Patient", f"Recall {pid} back into the waiting queue?"):
            if recall_patient(pid):
                messagebox.showinfo("Recalled", f"{pid} has been returned to the queue.")
                if update_stats_cb: update_stats_cb()
                refresh()

    refresh()
    btn = ttk.Frame(win); btn.pack(pady=8)
    ttk.Button(btn, text="Recall Patient", command=do_recall,
               bootstyle="success",          width=16).pack(side=LEFT, padx=6)
    ttk.Button(btn, text="Close",          command=win.destroy,
               bootstyle="secondary-outline", width=10).pack(side=LEFT, padx=6)
    
    # Main Window

# Main Window
def main_window(root, username, role):
    root.title("MediCare Patient Queue Management System")
    root.resizable(True, True)
    try:    root.state("zoomed")
    except: root.attributes("-zoomed", True)
    root.minsize(900, 600)
    root.maxsize(1920, 1080)

    hdr = ttk.Frame(root, bootstyle="primary", padding=(14, 8))
    hdr.pack(fill=X)
    ttk.Label(hdr, text="MediCare Community Clinic - Sierra Leone",
              font=("Tahoma", 13, "bold"),
              bootstyle="inverse-primary").pack(side=LEFT)
    
    ttk.Label(hdr, text=f"  {role}: {username}",
              font=("Tahoma", 11),
              bootstyle="inverse-primary").pack(side=LEFT, padx=16)
    clk = ttk.Label(hdr, text="", font=("Tahoma", 11),
                    bootstyle="inverse-primary")
    clk.pack(side=RIGHT)

    def tick():
        try:
            if not clk.winfo_exists():
                return
            clk.config(text=datetime.now().strftime("%H:%M:%S"))
            root.after(1000, tick)
        except tk.TclError:
            return 
    tick()

    # Stats cards
    stats_frame = ttk.Frame(root, padding=(14, 8))
    stats_frame.pack(fill=X)

    def make_card(parent, label, value, style):
        card = ttk.Frame(parent, bootstyle=style, padding=(14, 6))
        card.pack(side=LEFT, padx=(0, 12))
        ttk.Label(card, text=label, font=("Tahoma", 10),
                  bootstyle=f"inverse-{style}").pack()
        lbl = ttk.Label(card, text=str(value), font=("Tahoma", 15, "bold"),
                        bootstyle=f"inverse-{style}")
        lbl.pack()
        return lbl

    waiting_lbl = make_card(stats_frame, "Waiting",   len(patients), "warning")
    served_lbl  = make_card(stats_frame, "Served",    len(served),   "success")
    emerg_lbl   = make_card(stats_frame, "Emergency",
                            sum(1 for p in patients if p["category"] == "Emergency"), "danger")

    def update_stats():
        # Update all stat cards immediately after every action
        waiting_lbl.config(text=str(len(patients)))
        served_lbl.config(text=str(len(served)))
        emerg_lbl.config(text=str(sum(1 for p in patients if p["category"] == "Emergency")))

    ttk.Separator(root).pack(fill=X)

    menu = ttk.Frame(root, padding=20)
    menu.pack(fill=BOTH, expand=True)

    ttk.Label(menu, text="Patient Queue Management",
              font=("Tahoma", 16, "bold"),
              bootstyle="primary").pack(pady=(0, 6))
    ttk.Label(menu, text="Use the options below to manage the clinic queue",
              font=("Tahoma", 11),
              bootstyle="secondary").pack(pady=(0, 14))

    # Role-based access - each button lists which roles can see it
    buttons = [
        ("Register Patient",   "success",           lambda: open_register_dashboard(root, update_stats),
         ["Receptionist"]),
        ("View Queue",         "primary",           lambda: open_queue_dashboard(root, update_stats, role),
         ["Receptionist", "Nurse"]),
        ("Search Patient",     "info",              lambda: open_search_dashboard(root),
         ["Receptionist"]),
        ("Edit / Delete",      "warning-outline",   lambda: open_edit_dashboard(root, update_stats),
         ["Receptionist"]),
        ("Served Patients",    "success-outline",   lambda: open_served_dashboard(root, role),
         ["Receptionist", "Nurse"]),
        ("Summary",            "secondary-outline", lambda: open_summary_dashboard(root),
         ["Receptionist", "Nurse"]),
        ("Absent Patients",    "danger-outline",    lambda: open_absent_dashboard(root, update_stats),
         ["Receptionist", "Nurse"]),

        # Added - new feature dashboards
        ("Appointments",       "primary-outline",   lambda: open_appointment_dashboard(root),
         ["Receptionist"]),
        ("Search by Date",     "info-outline",      lambda: open_search_by_date_dashboard(root),
         ["Receptionist"]),
        ("Visit History",      "secondary-outline", lambda: open_visit_history_dashboard(root),
         ["Receptionist", "Nurse"]),
        ("Announcements",      "warning-outline",   lambda: open_announcements_dashboard(root, role),
         ["Receptionist", "Nurse"]),
        ("Activity Log",       "dark-outline",      lambda: open_activity_log_dashboard(root),
         ["Receptionist"]),
    ]

    for label, style, cmd, allowed_roles in buttons:
        if role in allowed_roles:
            ttk.Button(menu, text=label, 
                             command=cmd,
                             bootstyle=style, width=28).pack(pady=5)

    ttk.Separator(root).pack(fill=X)

    foot = ttk.Frame(root, padding=(10, 6)); foot.pack(fill=X)

    def on_exit():
        if messagebox.askyesno("Exit", "Exit MediQueue?"):
            save_session() # Added this
            auto_backup()
            root.destroy()

    def do_logout():
        if messagebox.askyesno("Logout", "Log out and return to the login screen?"):
            save_session() # Added this for saving when exisiting the program
            log_activity(f"{current_user[0]} logged out")
            current_user[0] = ""
            for widget in root.winfo_children():
                widget.destroy()
            show_login_screen(root, main_window)

    ttk.Button(foot, text="Logout", command=do_logout,
               bootstyle="warning-outline", width=12).pack(side=LEFT, padx=10)
    ttk.Button(foot, text="Exit", command=on_exit,
               bootstyle="danger-outline", width=12).pack(side=RIGHT, padx=10)

    update_stats()