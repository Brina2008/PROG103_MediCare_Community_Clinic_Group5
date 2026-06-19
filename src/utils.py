from datetime import datetime
import hashlib

# Constants
PRIORITY = {"Emergency": 1, "Pregnant": 2, "Normal": 3}
AVG_MIN = 5
WAIT_ALERT_MIN = 45   
STAFF_FILE     = "staff_accounts.csv"
ACTIVITY_FILE      = "activity_log.csv"
ANNOUNCEMENTS_FILE = "announcements.txt"
APPOINTMENTS_FILE  = "appointments.csv"
SESSION_FILE  = "Session_backup.csv"

FIELDNAMES = ["id", "name", 
              "age", "gender", 
              "contact", "complaint",
              "arrived", "category",
              "queue_no", "status"]

APPT_FIELDS = ["name", "contact", "date", "time", "note", "booked_by"]

# Security
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Validation
def ok_name(t):      return bool(t.strip()) and t.replace(" ", "").isalpha()
def ok_age(t):       return t.isdigit() and 0 <= int(t) <= 120
def ok_note(t):      return bool(t.strip()) and not t.strip().isdigit()

def ok_time(t):
    return (len(t) == 5 and t[2] == ":" and t[:2].isdigit() and t[3:].isdigit()
            and 0 <= int(t[:2]) <= 23 and 0 <= int(t[3:]) <= 59)

def ok_complaint(t): return bool(t.strip()) and not t.strip().isdigit() and len(t.strip()) >= 3
def ok_contact(t):   return t.isdigit() and 7 <= len(t) <= 15