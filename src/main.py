""" Patient Queue Management System - MediCare Community Clinic, Sierra Leone"""

# Import GUI Components
from gui import *

# Entry Point

if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    show_login_screen(root, main_window)
    root.mainloop()