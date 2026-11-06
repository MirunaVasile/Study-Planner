# Study-Planner

<p align="center">
  A desktop app that helps students organize their courses, track assignment deadlines and measure their study time, with an admin panel and visual progress reports.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/GUI-Tkinter-6f42c1" />
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/Charts-Matplotlib-11557c" />
  <img src="https://img.shields.io/badge/Tests-15%20passing-brightgreen" />
  <img src="https://img.shields.io/badge/Coverage-95%25-brightgreen" />
</p>

---

## ✨ Overview

**Study Planner** is a Python desktop application built as a Software Systems Engineering project. It covers the full process: requirements and use cases, UML modelling (class and sequence diagrams), implementation, and automated testing.

Students sign up, add their courses, register deadlines for assignments and exams, and run timed study sessions. A progress dashboard turns all of that into statistics and charts. An administrator account can manage global settings and see all registered users.

## Features

###  For students

| Module | What you can do |
|---|---|
| **🔐 Authentication** | Register a new account, log in, and edit your profile (name, email, password). |
| **📖 Courses** | Add, edit and delete courses with name, professor, credits and a color label picked from a 5-color pastel palette. Deleting a course also removes its deadlines and sessions. |
| **⏰ Deadlines & Calendar** | Add deadlines with a title, description, linked course and due date. A monthly calendar view shows what is coming up, and tasks can be marked as completed. |
| **⏱️ Study Sessions** | A built-in timer with a configurable target duration (or open-ended with "I don't know"), quick-pick time suggestions, notes, pause/resume, postpone, and finish. Unfinished sessions can be continued later. |
| **📊 Progress Report** | KPI cards (total time studied, top course, completed tasks) plus three charts: time per course, deadline status, and study evolution over the last 7 days. |

###  For administrators

- A dedicated control panel instead of the student interface.
- Edit the **study-time suggestions** (e.g. `15, 30, 45, 60` minutes) shown to every student when starting a session.
- View the list of all registered users.

##  Architecture

The project follows a layered design, which keeps the UI free of SQL and makes the business logic easy to unit test.

```
┌──────────────────────────────────────────────┐
│  UI layer (Tkinter)                          │
│  LoginFrame · RegisterFrame · MainAppFrame   │
│  DisciplinePage · DeadlinesPage              │
│  StudySessionsPage · ProgressPage            │
└───────────────────┬──────────────────────────┘
                    │
┌───────────────────▼──────────────────────────┐
│  Service layer (business logic)              │
│  AuthService · PlannerService                │
└───────────────────┬──────────────────────────┘
                    │
┌───────────────────▼──────────────────────────┐
│  Repository layer (data access)              │
│  StudentRepo · DisciplinaRepo · DeadlineRepo │
│  StudySessionRepo                            │
└───────────────────┬──────────────────────────┘
                    │
              ┌─────▼─────┐
              │  SQLite   │
              └───────────┘
```

### Database schema

| Table | Purpose |
|---|---|
| `studenti` | Users (name, unique email, password, role: `student` / `admin`) |
| `discipline` | Courses belonging to a student |
| `deadlines` | Tasks linked to a course, with due date and status |
| `sesiuni_studiu` | Study sessions with actual and target duration, notes and status |
| `setari` | Global key-value settings managed by the admin |

### UML class diagram

<p align="center">
  <img src="docs/class_diagram.png" alt="Class diagram" width="85%" />
</p>

## 📁 Project structure

```
study_planner/
├── main.py                 # Entry point, wires DB, repositories, services and UI
├── backend.py              # Database, repositories and services
├── config.py               # Colors, fonts and the course color palette
├── login_page.py           # Login screen
├── register_page.py        # Sign-up screen
├── dashboard_page.py       # Main shell: sidebar, profile, admin panel
├── discipline_page.py      # Courses management
├── deadlines_page.py       # Deadlines list and calendar
├── study_sessions_page.py  # Study sessions and timer window
├── progress_page.py        # KPIs and Matplotlib charts
├── run_tests.py            # Test runner
└── teste/                  # Unit tests
    ├── test_auth.py
    ├── test_discipline.py
    ├── test_deadlines.py
    └── test_sessions.py
```

## ⚙️ Getting started

### Requirements

- Python **3.9+** (Tkinter and SQLite ship with the standard installer)
- [Matplotlib](https://matplotlib.org/) for the progress charts

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/study_planner.git
cd study_planner

# 2. (Optional) create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install the dependencies
pip install matplotlib

# 4. Run the app
python main.py
```

The SQLite database (`studyplanner.db`) is created automatically on first launch.

### Default administrator account

| Email | Password |
|---|---|
| `admin` | `admin` |

> ⚠️ Change this account's credentials if you ever deploy the app beyond a local demo (see [Known limitations](#-known-limitations)).

## 🧪 Testing

The project includes **15 unit tests** covering authentication, courses, deadlines and study sessions. Each test runs against an isolated database.

```bash
python run_tests.py
```

To measure coverage:

```bash
pip install coverage
coverage run run_tests.py
coverage report -m
coverage html        # opens a detailed report in htmlcov/
```

Statement coverage of the business logic in `backend.py` is **95%**.

| Test suite | Scenarios |
|---|---|
| `test_auth.py` | Successful registration · successful login · login with wrong password |
| `test_discipline.py` | Create · create without name (rejected) · edit · delete |
| `test_deadlines.py` | Create · create without title (rejected) · edit · mark as completed · delete |
| `test_sessions.py` | Save new session · resume an existing session · delete |

## 📐 Software engineering artifacts

This app was developed alongside its engineering documentation:

- **Use cases** written with an adapted Cockburn template (ID, actors, preconditions, postconditions, normal / alternative / exception flows), extended with **method-level traceability** to the code.
- **UML class diagram** of entities, UI, services and repositories.
- **UML sequence diagrams** for the main flows: add / edit / delete course, add / edit / delete deadline, start / continue / delete study session, view progress, and admin settings.
- **Research and test cases** defined before implementation and later automated as unit tests.


---

<p align="center">Made with 💜 and a lot of coffee ☕</p>
