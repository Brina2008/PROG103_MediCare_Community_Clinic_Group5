# 🏥 MediQueue – Patient Queue Management System

A Python-based GUI application designed to manage patient queues in community clinics across Sierra Leone. Built using Tkinter and ttkbootstrap, the system supports efficient patient registration, prioritization, queue management, and reporting while aligning with SDG 3 (Good Health and Well-being).

---

## 📌 Overview

MediQueue is a desktop application developed for healthcare facilities to improve patient flow and reduce waiting times. The system allows clinic staff to register patients, prioritize emergencies, manage queues, search records, and generate summaries.

This project was developed as a final submission for the Principles of Structured Programming course and demonstrates the use of structured programming concepts, GUI design, input validation, and real-world problem-solving.

---

## 🎯 Sustainable Development Goal

**SDG 3 – Good Health and Well-being**

MediQueue supports quality healthcare delivery by improving patient organization, reducing waiting times, and ensuring emergency cases receive priority attention.

---

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

---

## 🌍 Real-World Impact

MediQueue is designed to support clinics and healthcare centers across Sierra Leone by:

Reducing patient waiting times
Improving queue organization
Prioritizing emergency cases
Enhancing healthcare service delivery
Supporting digital transformation in healthcare

---

## 👥 Authors

* Sabrina Kandeh
* Ameynor Salma Kamara
* Alfreda Victoria Dumbuya
---

## 🧰 Technology Stack

Language: Python 3
GUI Framework: Tkinter
GUI Theme Library: ttkbootstrap
Data Storage: Python Lists and Dictionaries
Data Export: CSV Files

---

## 📄 License

This project is licensed under the MIT License. See the LICENSE.md file for details.

---

## 🚀 How to Run the Project

### 1. Install Python

Ensure Python 3 is installed on your computer.

### 2. Install ttkbootstrap

```bash
pip install ttkbootstrap
```

### 3. Run the Application

```bash
python main.py
```
---

**MediQueue – Improving Patient Flow for Better Healthcare in Sierra Leone 🇸🇱**