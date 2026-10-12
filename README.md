# Pulse Gym Membership Management System 🏋️‍♂️

A beginner-friendly, clean, and reliable **Gym Membership Management System** built with **Python**, **Flask**, and **SQLite**. Designed for gym owners and staff to easily manage member records, track membership plans, record payments, and monitor active vs. expired status.

---

## ✨ Features

- **📊 Dashboard Overview**: Real-time KPI statistics (Total Members, Active, Expired, Pending Payments) and recent registration alerts.
- **➕ Member Registration**: Add new gym members with form validation (Name, Age [1-120], Phone, Plan, Start Date). Automatically assigns unique Member IDs (`GYM-1001`, `GYM-1002`, ...).
- **⏱️ Auto-Calculated Expiration Dates**: Computes plan expiration dates automatically:
  - Monthly: +1 Month
  - 3 Months: +3 Months
  - 6 Months: +6 Months
  - 1 Year: +1 Year
- **⚡ Live Search**: Search members in real-time by **Member ID**, **Full Name**, or **Phone Number** across both the dedicated Search page and Member Directory.
- **📝 Member Record Management**: Update member details or delete records with confirmation prompts.
- **💳 Payment Logging & Renewals**: Record membership payments (₱), update payment status (`Paid`, `Pending`, `Overdue`), and renew or extend membership duration.
- **🛡️ Status Monitor**: Real-time tracking of Active vs. Expired members based on the current calendar date.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.x, Flask
- **Database**: SQLite3 (`gym_management.db`)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript, FontAwesome

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure you have **Python 3.9+** installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/<your-username>/GymManagementSystem.git
cd GymManagementSystem
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```
Open your web browser and navigate to:
**`http://127.0.0.1:5000`**

*(On Windows, you can also simply double-click `run_app.bat`)*

---

## 🧪 Running Automated Tests

Run the built-in test suite:
```bash
python -m unittest test_system.py
```

All 8 tests verify date mathematics, automatic membership status transitions, CRUD operations, and form validation.

---

## 📂 Project Structure

```
GymManagementSystem/
├── app.py                  # Core Flask web server & routing
├── database.py             # SQLite helper functions & schema setup
├── sample_data.py          # Seed script for initial sample data
├── test_system.py          # Automated unit test suite
├── requirements.txt        # Python package dependencies
├── run_app.bat             # 1-click Windows launcher
├── run_public_tunnel.bat   # 1-click mobile tunnel launcher
├── templates/              # HTML Templates (Dashboard, Members, Search, etc.)
└── static/                 # CSS styling & interactive JavaScript
```

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
