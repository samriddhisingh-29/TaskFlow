# TaskFlow — Smart Task & Project Management Dashboard

> *"Plan better. Work smarter."*

TaskFlow is a modern, responsive full-stack task and project management dashboard engineered with Python, Flask, SQLite, SQLAlchemy, and Chart.js.

Designed with clean white surfaces, soft lavender/purple accents, warm amber alerts, and emerald completion indicators, TaskFlow combines the refined user experience of a modern SaaS productivity tool with transparent, beginner-accessible Python fundamentals.

---

## 🎓 Educational Architecture & Purpose

This project is built directly upon the foundational learning objectives of **Project 1: To-Do List**, elevating volatile console scripts into an enterprise-grade full-stack web application:

* **Python Lists & `list.append()`**: Database records are translated in the service layer (`app/services.py`) into Python dictionaries and assembled into native Python lists using explicit loops and `list.append()`.
* **Collection Iteration & Loops**: Dynamic counting, status tallies, and multi-day velocity trends are processed using clear `for` loops and comprehensions.
* **Input → Process → Output**:
  * **Input**: Web forms, search queries, filter arguments, and JSON payloads.
  * **Process**: Validation, collection transformations, business calculations, and database transactions.
  * **Output**: Responsive Jinja2 HTML views, dynamic CSV streams, and Chart.js JSON analytics.
* **Persistence over Volatile Memory**: Seamless transition from in-memory task lists to persistent relational tables powered by SQLite and SQLAlchemy.
* **Dynamic Calculations**: Zero hardcoded stats. Total, completed, in-progress, overdue counts, and completion percentages are calculated dynamically in Python with zero-division safety.

---

## 🚀 Key Features

* **Interactive Dashboard**:
  * Real-time productivity metrics (Total Tasks, Completed, In Progress, Overdue).
  * Overall completion percentage bar.
  * Weekly velocity bar chart & live status doughnut chart powered by Chart.js.
  * Recent task activities and upcoming deadlines widget.
  * Quick status toggling with instant visual feedback.
* **Task Management**:
  * Full CRUD (Create, Read, Update, Delete) for tasks.
  * Multi-field search across title, description, project, and category.
  * Filtering by status (`TODO`, `IN_PROGRESS`, `COMPLETED`), priority (`LOW`, `MEDIUM`, `HIGH`, `URGENT`), and category.
  * Sorting by due date, priority weighting, creation date, and alphabetical title.
* **Project Hub & Detail Views**:
  * Project cards with task counts and live progress bars.
  * Dedicated Project Detail page with an SVG progress ring and isolated task breakdown.
  * Relational cascade delete ensuring database integrity.
* **Productivity Intelligence & Reports**:
  * 4 dynamic Chart.js visualizations synchronized asynchronously via `/api/analytics`.
  * Category workload distribution analysis.
* **Dynamic In-Memory CSV Export**:
  * `/tasks/export` route generating structured CSV downloads on the fly without third-party dependencies.
* **UI/UX Design System**:
  * Responsive layout for Mobile, Tablet, and Desktop.
  * Professional **Dark Mode** toggle persisted via `localStorage` through CSS custom properties.
  * Keyboard-accessible modals, toast alerts, and empty states.
  * Custom user-friendly error handlers (`404.html` and `500.html`).

---

## 🛠️ Tech Stack

* **Backend**: Python 3.11+, Flask 3.1+, Flask-SQLAlchemy 3.1+, SQLite
* **Frontend**: HTML5, CSS3 Custom Properties, Vanilla JavaScript (ES6+), Chart.js (v4)
* **Testing**: pytest 9+
* **Environment & Config**: python-dotenv, Virtual Environments (`venv`)

---

## 📁 Project Architecture

```text
to-do/
├── app/
│   ├── __init__.py           # Flask application factory, error handlers, Jinja filters
│   ├── models.py             # SQLAlchemy models (Project, Task) with relational constraints
│   ├── routes.py             # HTTP routes, request parsing, response formatting
│   ├── services.py           # Educational service layer (list operations, CRUD, math)
│   ├── templates/
│   │   ├── base.html         # Application shell, navigation, modals, toasts, theme script
│   │   ├── dashboard.html    # Dashboard metrics, weekly chart, recent tasks
│   │   ├── tasks.html        # Comprehensive task management, search, and filters
│   │   ├── projects.html     # Projects grid and project creation modal
│   │   ├── project_detail.html # Project deep-dive with SVG progress ring
│   │   ├── reports.html      # Chart.js analytics report dashboard
│   │   ├── 404.html          # Custom 404 Not Found error template
│   │   └── 500.html          # Custom 500 Internal Server Error template
│   └── static/
│       ├── css/
│       │   └── style.css     # CSS custom properties, light/dark themes, responsive grid
│       └── js/
│           ├── app.js        # Dark mode, mobile sidebar, toast utility, modal controls
│           ├── tasks.js      # Asynchronous status toggles, edit prefill, delete modals
│           └── charts.js     # Chart.js dynamic initialization from /api/analytics
├── instance/                 # Local SQLite database storage (taskflow.db)
├── tests/
│   ├── conftest.py           # Pytest fixtures and isolated in-memory test database
│   ├── test_tasks.py         # Tests for validation, creation, editing, toggling, filtering
│   ├── test_projects.py      # Tests for projects, details math, and cascade delete
│   └── test_dashboard.py     # Tests for dashboard calculations, analytics API, CSV export
├── .env.example              # Environment variables template
├── .gitignore                # Production gitignore rules
├── config.py                 # Multi-environment configuration classes
├── pytest.ini                # Pytest configuration
├── requirements.txt          # Python dependencies
├── run.py                    # Application entry point with automatic database seeding
└── README.md                 # Complete project documentation
```

---

## ⚙️ Installation & Setup

### 1. Clone or Open the Workspace
```powershell
cd c:\Users\samri\Downloads\to-do
```

### 2. Set Up Virtual Environment
```powershell
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows Command Prompt:
.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Run the Application
```powershell
python run.py
```
Upon startup, TaskFlow will automatically create the SQLite tables and populate realistic sample projects and tasks if the database is newly created.

Open your browser at:
```text
http://127.0.0.1:5000
```

---

## 🧪 Automated Testing

Execute the complete test suite with `pytest`:
```powershell
pytest -v
```

All 15 automated test cases verify:
* Input validation rules (length constraints, required fields, enum choices).
* Task and Project creation and persistence.
* Task status toggling and field updates.
* Cascade deletion of child tasks when a project is removed.
* Division-by-zero protection in dashboard calculations.
* Real-time JSON output from the analytics endpoint.
* Dynamic CSV export format and column headers.

---

## 📦 GitHub Deployment & Publishing Instructions

When you are ready to publish TaskFlow to GitHub, run the following commands:

```bash
# 1. Initialize git repository
git init

# 2. Stage all project files
git add .

# 3. Create initial commit
git commit -m "Initial commit: TaskFlow project"

# 4. Set default branch to main
git branch -M main

# 5. Connect to your GitHub repository
git remote add origin YOUR_GITHUB_REPOSITORY_URL

# 6. Push to GitHub
git push -u origin main
```

*(Note: Never commit sensitive credentials or your local database. These are excluded by `.gitignore`.)*

---

## 🔮 Future Improvements

1. User Authentication (Registration, Login, Multi-tenant task separation).
2. Email or Browser notifications for tasks approaching their due date.
3. Subtasks and checklist items within tasks.
4. Drag-and-drop Kanban board view.
