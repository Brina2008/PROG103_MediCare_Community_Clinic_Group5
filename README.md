# 🏥 MediQueue - Patient Management System

MediQueue is a Python GUI application that helps manage patient queues efficiently while supporting SDG 3 (Good Health and Well-being).

## 📌 Overview

MediQueue is a desktop application developed for healthcare facilities to improve patient flow and reduce waiting times. The system allows clinic staff to register patients, prioritize emergencies, manage queues, search records, and generate summaries.

This project was developed as a final submission for the Principles of Structured Programming course and demonstrates the use of structured programming concepts, GUI design, input validation, and real-world problem-solving.



## 🎯 Sustainable Development Goal

**SDG 3 - Good Health and Well-being**

MediQueue supports quality healthcare delivery by improving patient organization, reducing waiting times, and ensuring emergency cases receive priority attention.



## ✨ Features

### Receptionist & Nurse Login

* Secure staff registration and login
* Role-based access (Receptionist and Nurse)
* Password-protected accounts

### Patient Registration

* Automatic Patient ID generation
* Capture patient name, age, gender, and contact number
* Record patient complaints
* Assign priority categories:

  * Emergency
  * Pregnant
  * Normal
* Automatic queue positioning
* Estimated waiting time calculation

### Queue Management

* View live patient queue
* Priority-based sorting
* Call next patient
* Undo accidental patient calls
* Real-time queue updates

### Patient Search

* Search patients by ID or name
* View patient status (Waiting or Served)

### Edit and Delete Records

* Update patient information
* Delete patient records
* Validate all changes before saving

### Served Patients Dashboard

* View served patients
* Clear served records
* Export served records to CSV

### Summary Dashboard

* Total patients registered
* Patients waiting
* Patients served
* Emergency, Pregnant, and Normal patient statistics
* Next patient information

### Data Management

* CSV Export functionality
* Automatic daily backup generation
* In-memory storage using Python lists and dictionaries     
     
  
 
## 🌍 Real-World Impact

* Reducing patient waiting times
* Improving queue organization
* Prioritizing emergency cases
* Enhancing healthcare service delivery


## 👥 Authors

* Sabrina Kandeh
* Ameynor Salma Kamara
* Alfreda Victoria Dumbuya


## 🧰 Technology Stack

* Language: Python 3
* GUI Framework: Tkinter
* GUI Theme Library: ttkbootstrap
* Data Storage: Python Lists and Dictionaries
* Data Export: CSV Files
* License: MIT

## Screen Shot

*  Login Screen Page

<img src="./screenshots/Screenshot 2026-06-20 025926.png" alt="login" width="600" >

* Receptionist login Dashboard page

<img src="./screenshots/Screenshot 2026-06-19 065254.png" alt="Rectionist" width="600">

* Patient Register page

<img src="./screenshots/Screenshot 2026-06-19 064304.png" alt="patient register" width="600">

* Patient Served summary Queue Page

<img src="./screenshots/Screenshot 2026-06-19 070349.png" alt="patient summary" width="600">

* Nurse login Page

<img src="./screenshots/Screenshot 2026-06-19 065716.png" alt="nurse" width="600">


## 🔒 Validation Features

The system validates:

* Patient names
* Age range (0–120)
* Contact numbers
* Complaint descriptions
* Time format (HH:MM)
* Category selection

This helps maintain data accuracy and reliability.


## 🚀 How to Run the Project

### 1. Install Python

Ensure Python 3 is installed on your computer, Then install the extra libaray ttkbootstrap:

```bash
pip install ttkbootstrap
```

### 2. Download Repository

```bash
git clone https://github.com/Brina2008/PROG103_MediCare_Community_Clinic_Group5.git
cd PROG103_MediCare_Clinic_Group5
cd src
```

### 3. Run the Application

```bash
python main.py
```
 