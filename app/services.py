"""
TaskFlow Service Layer — Educational & Business Logic Architecture
==================================================================

ARCHITECTURE: INPUT -> PROCESS -> OUTPUT
- INPUT: User parameters received via web requests (forms, JSON, query params).
- PROCESS: Data validation, transformation into Python data structures (lists, dicts),
           collection manipulation (append, loops, filtering, sorting, aggregations),
           and database persistence via SQLAlchemy.
- OUTPUT: Standardized Python dictionaries and lists returned to Flask routes for
          rendering via Jinja2 templates or serialization to JSON APIs.

This module explicitly bridges the original "Project 1: To-Do List" collection concepts
(Python lists, list.append(), loops, dictionaries) with modern full-stack web architecture.
"""

from datetime import datetime, date, timedelta, timezone
from app.models import db, Task, Project, VALID_PRIORITIES, VALID_TASK_STATUSES, VALID_PROJECT_STATUSES

# ==============================================================================
# 1. DATA TRANSFORMATION & LIST COLLECTION (Demonstrating list.append & loops)
# ==============================================================================

def get_all_tasks_as_list():
    """
    Retrieves all tasks from the database and constructs a Python list of dictionaries.
    
    [LEARNING CONCEPT]:
    Explicitly demonstrates Python list initialization, iterating with a for-loop,
    dictionary creation, and list.append().
    """
    # PROCESS: Query raw database objects
    db_tasks = Task.query.order_by(Task.created_at.desc()).all()
    
    # 1. Initialize an empty Python list
    tasks_list = []
    
    # 2. Iterate using a standard Python for-loop
    for task in db_tasks:
        # 3. Construct a dictionary representing task state
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description or "",
            "status": task.status,
            "priority": task.priority,
            "category": task.category,
            "due_date": task.due_date.strftime("%Y-%m-%d") if task.due_date else None,
            "created_at": task.created_at.strftime("%Y-%m-%d %H:%M") if task.created_at else None,
            "updated_at": task.updated_at.strftime("%Y-%m-%d %H:%M") if task.updated_at else None,
            "project_id": task.project_id,
            "project_name": task.project.name if task.project else "No Project",
            "is_overdue": task.is_overdue
        }
        
        # 4. Use list.append() to accumulate task items into the collection
        tasks_list.append(task_dict)
        
    # OUTPUT: Return the completed Python list
    return tasks_list


def filter_and_sort_tasks(tasks, search_query=None, status_filter=None, priority_filter=None, category_filter=None, sort_by="created_desc"):
    """
    Filters and sorts a collection of task dictionaries using native Python collection operations.
    
    [LEARNING CONCEPT]:
    Demonstrates Python conditionals, string operations, list filtering, and lambda sorting.
    """
    # PROCESS: Filtering phase using a loop or list comprehension
    filtered_tasks = []
    
    for task in tasks:
        # Search query matching: Title, Description, Project, Category
        if search_query:
            query = search_query.strip().lower()
            matches_title = query in task["title"].lower()
            matches_desc = query in task["description"].lower()
            matches_proj = query in task["project_name"].lower()
            matches_cat = query in task["category"].lower()
            if not (matches_title or matches_desc or matches_proj or matches_cat):
                continue
        
        # Status filter
        if status_filter and status_filter != "ALL":
            if task["status"] != status_filter:
                continue
                
        # Priority filter
        if priority_filter and priority_filter != "ALL":
            if task["priority"] != priority_filter:
                continue
                
        # Category filter
        if category_filter and category_filter != "ALL":
            if task["category"].lower() != category_filter.lower():
                continue
                
        # If all criteria match, append to filtered results
        filtered_tasks.append(task)
        
    # PROCESS: Sorting phase using Python's sorted() and key functions
    priority_order = {"URGENT": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    
    if sort_by == "due_date_asc":
        # Sort items with due_dates first, None dates at the end
        filtered_tasks = sorted(
            filtered_tasks,
            key=lambda t: (t["due_date"] is None, t["due_date"] or "")
        )
    elif sort_by == "due_date_desc":
        filtered_tasks = sorted(
            filtered_tasks,
            key=lambda t: (t["due_date"] is None, t["due_date"] or ""),
            reverse=True
        )
    elif sort_by == "priority_desc":
        filtered_tasks = sorted(
            filtered_tasks,
            key=lambda t: priority_order.get(t["priority"], 0),
            reverse=True
        )
    elif sort_by == "priority_asc":
        filtered_tasks = sorted(
            filtered_tasks,
            key=lambda t: priority_order.get(t["priority"], 0)
        )
    elif sort_by == "title_asc":
        filtered_tasks = sorted(filtered_tasks, key=lambda t: t["title"].lower())
    else:  # default 'created_desc'
        filtered_tasks = sorted(filtered_tasks, key=lambda t: t["id"], reverse=True)
        
    # OUTPUT: Return filtered and sorted Python list
    return filtered_tasks


# ==============================================================================
# 2. DYNAMIC DASHBOARD CALCULATIONS (Mathematical & Aggregation Logic)
# ==============================================================================

def calculate_dashboard_metrics(tasks_list=None):
    """
    Computes summary metrics dynamically from the task collection.
    
    [LEARNING CONCEPT]:
    Demonstrates counting with loops/comprehensions, zero-division protection,
    and structured dictionary aggregation.
    """
    # INPUT: If tasks_list is not provided, fetch current tasks
    if tasks_list is None:
        tasks_list = get_all_tasks_as_list()
        
    total_tasks = len(tasks_list)
    completed_tasks = 0
    in_progress_tasks = 0
    todo_tasks = 0
    overdue_tasks = 0
    
    # PROCESS: Iterate through list and accumulate counts
    for task in tasks_list:
        status = task["status"]
        if status == "COMPLETED":
            completed_tasks += 1
        elif status == "IN_PROGRESS":
            in_progress_tasks += 1
        elif status == "TODO":
            todo_tasks += 1
            
        if task.get("is_overdue", False):
            overdue_tasks += 1

    pending_tasks = todo_tasks + in_progress_tasks
    
    # Division-by-zero protection for completion percentage
    if total_tasks > 0:
        completion_percentage = round((completed_tasks / total_tasks) * 100, 1)
    else:
        completion_percentage = 0.0

    # Count active projects
    active_projects_count = Project.query.filter_by(status="ACTIVE").count()

    # OUTPUT: Metric summary dictionary
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "todo_tasks": todo_tasks,
        "pending_tasks": pending_tasks,
        "overdue_tasks": overdue_tasks,
        "completion_percentage": completion_percentage,
        "active_projects": active_projects_count
    }


def get_analytics_data():
    """
    Calculates dynamic datasets for Chart.js charts and reports.
    Computes:
    1. Status distribution (TODO, IN_PROGRESS, COMPLETED)
    2. Priority distribution (LOW, MEDIUM, HIGH, URGENT)
    3. Category distribution
    4. Weekly task completion / creation trends (last 7 days)
    5. Project progress summary
    """
    tasks = get_all_tasks_as_list()
    projects = Project.query.all()
    
    # 1. Status Distribution
    status_counts = {"TODO": 0, "IN_PROGRESS": 0, "COMPLETED": 0}
    # 2. Priority Distribution
    priority_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "URGENT": 0}
    # 3. Category Distribution
    category_counts = {}

    for task in tasks:
        # Status tally
        st = task.get("status")
        if st in status_counts:
            status_counts[st] += 1
            
        # Priority tally
        pr = task.get("priority")
        if pr in priority_counts:
            priority_counts[pr] += 1
            
        # Category tally
        cat = task.get("category", "General")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # 4. Weekly Trend (Past 7 Days)
    today = date.today()
    weekly_labels = []
    weekly_created = []
    weekly_completed = []
    
    # Generate days in chronological order
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        weekly_labels.append(day.strftime("%a (%b %d)"))
        
        # Count tasks created on this day
        created_count = 0
        completed_count = 0
        for task in tasks:
            if task.get("created_at") and task["created_at"].startswith(day_str):
                created_count += 1
            # If completed on or around this day (updated_at)
            if task.get("status") == "COMPLETED" and task.get("updated_at") and task["updated_at"].startswith(day_str):
                completed_count += 1
                
        weekly_created.append(created_count)
        weekly_completed.append(completed_count)

    # 5. Project Progress Data
    project_progress = []
    for proj in projects:
        proj_tasks = [t for t in tasks if t["project_id"] == proj.id]
        total_p_tasks = len(proj_tasks)
        completed_p_tasks = len([t for t in proj_tasks if t["status"] == "COMPLETED"])
        progress_pct = round((completed_p_tasks / total_p_tasks * 100), 1) if total_p_tasks > 0 else 0.0
        
        project_progress.append({
            "id": proj.id,
            "name": proj.name,
            "status": proj.status,
            "total_tasks": total_p_tasks,
            "completed_tasks": completed_p_tasks,
            "progress_percentage": progress_pct
        })

    return {
        "status_distribution": status_counts,
        "priority_distribution": priority_counts,
        "category_distribution": category_counts,
        "weekly_trend": {
            "labels": weekly_labels,
            "created": weekly_created,
            "completed": weekly_completed
        },
        "project_progress": project_progress
    }


# ==============================================================================
# 3. TASK CRUD SERVICE FUNCTIONS
# ==============================================================================

def validate_task_data(data):
    """
    Validates user input before database creation or update.
    Returns (is_valid, error_message or dict of cleaned data).
    """
    title = data.get("title", "").strip() if data.get("title") else ""
    if not title:
        return False, "Task title is required."
    if len(title) < 3:
        return False, "Task title must be at least 3 characters long."
    if len(title) > 150:
        return False, "Task title cannot exceed 150 characters."

    status = data.get("status", "TODO").upper()
    if status not in VALID_TASK_STATUSES:
        return False, f"Invalid status: {status}. Must be one of {VALID_TASK_STATUSES}."

    priority = data.get("priority", "MEDIUM").upper()
    if priority not in VALID_PRIORITIES:
        return False, f"Invalid priority: {priority}. Must be one of {VALID_PRIORITIES}."

    category = data.get("category", "General").strip() or "General"
    description = data.get("description", "").strip()

    # Parse due_date safely
    due_date = None
    due_date_str = data.get("due_date")
    if due_date_str:
        if isinstance(due_date_str, date):
            due_date = due_date_str
        elif isinstance(due_date_str, str) and due_date_str.strip():
            try:
                due_date = datetime.strptime(due_date_str.strip(), "%Y-%m-%d").date()
            except ValueError:
                return False, "Invalid due date format. Expected YYYY-MM-DD."

    # Parse project_id
    project_id = data.get("project_id")
    if project_id and str(project_id).strip():
        try:
            project_id = int(project_id)
            if not db.session.get(Project, project_id):
                return False, f"Project with ID {project_id} does not exist."
        except ValueError:
            return False, "Project ID must be a valid integer."
    else:
        project_id = None

    cleaned_data = {
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "category": category,
        "due_date": due_date,
        "project_id": project_id
    }
    return True, cleaned_data


def create_task(data):
    """Creates a new Task record after rigorous validation."""
    is_valid, result = validate_task_data(data)
    if not is_valid:
        return None, result

    task = Task(
        title=result["title"],
        description=result["description"],
        status=result["status"],
        priority=result["priority"],
        category=result["category"],
        due_date=result["due_date"],
        project_id=result["project_id"]
    )
    db.session.add(task)
    db.session.commit()
    return task, None


def update_task(task_id, data):
    """Updates an existing Task record."""
    task = db.session.get(Task, task_id)
    if not task:
        return None, f"Task with ID {task_id} not found."

    is_valid, result = validate_task_data(data)
    if not is_valid:
        return None, result

    task.title = result["title"]
    task.description = result["description"]
    task.status = result["status"]
    task.priority = result["priority"]
    task.category = result["category"]
    task.due_date = result["due_date"]
    task.project_id = result["project_id"]
    task.updated_at = datetime.now(timezone.utc)

    db.session.commit()
    return task, None


def toggle_task_status(task_id):
    """
    Toggles task status between COMPLETED and TODO/IN_PROGRESS.
    Demonstrates state transition logic.
    """
    task = db.session.get(Task, task_id)
    if not task:
        return None, f"Task with ID {task_id} not found."

    if task.status == "COMPLETED":
        task.status = "TODO"
    else:
        task.status = "COMPLETED"

    task.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return task, None


def delete_task(task_id):
    """Deletes a Task record."""
    task = db.session.get(Task, task_id)
    if not task:
        return False, f"Task with ID {task_id} not found."

    db.session.delete(task)
    db.session.commit()
    return True, None


# ==============================================================================
# 4. PROJECT CRUD & DETAIL SERVICE FUNCTIONS
# ==============================================================================

def validate_project_data(data):
    """Validates project input parameters."""
    name = data.get("name", "").strip() if data.get("name") else ""
    if not name:
        return False, "Project name is required."
    if len(name) < 2:
        return False, "Project name must be at least 2 characters long."
    if len(name) > 100:
        return False, "Project name cannot exceed 100 characters."

    status = data.get("status", "ACTIVE").upper()
    if status not in VALID_PROJECT_STATUSES:
        return False, f"Invalid project status: {status}."

    description = data.get("description", "").strip()

    deadline = None
    deadline_str = data.get("deadline")
    if deadline_str:
        if isinstance(deadline_str, date):
            deadline = deadline_str
        elif isinstance(deadline_str, str) and deadline_str.strip():
            try:
                deadline = datetime.strptime(deadline_str.strip(), "%Y-%m-%d").date()
            except ValueError:
                return False, "Invalid deadline date format. Expected YYYY-MM-DD."

    return True, {
        "name": name,
        "description": description,
        "status": status,
        "deadline": deadline
    }


def create_project(data):
    """Creates a new Project record."""
    is_valid, result = validate_project_data(data)
    if not is_valid:
        return None, result

    project = Project(
        name=result["name"],
        description=result["description"],
        status=result["status"],
        deadline=result["deadline"]
    )
    db.session.add(project)
    db.session.commit()
    return project, None


def get_project_details(project_id):
    """
    Retrieves project details along with its calculated task statistics and task list.
    """
    project = db.session.get(Project, project_id)
    if not project:
        return None

    tasks_raw = project.tasks
    tasks_list = []
    completed_count = 0
    in_progress_count = 0
    todo_count = 0
    overdue_count = 0

    for task in tasks_raw:
        task_data = task.to_dict()
        tasks_list.append(task_data)
        
        if task.status == "COMPLETED":
            completed_count += 1
        elif task.status == "IN_PROGRESS":
            in_progress_count += 1
        elif task.status == "TODO":
            todo_count += 1
            
        if task.is_overdue:
            overdue_count += 1

    total_tasks = len(tasks_list)
    progress_percentage = round((completed_count / total_tasks * 100), 1) if total_tasks > 0 else 0.0

    return {
        "project": project,
        "tasks": tasks_list,
        "total_tasks": total_tasks,
        "completed_tasks": completed_count,
        "pending_tasks": in_progress_count + todo_count,
        "in_progress_tasks": in_progress_count,
        "todo_tasks": todo_count,
        "overdue_tasks": overdue_count,
        "progress_percentage": progress_percentage
    }


# ==============================================================================
# 5. REALISTIC SEED DATA GENERATOR
# ==============================================================================

def seed_sample_data():
    """
    Populates realistic sample projects and tasks if the database is currently empty.
    Adheres strictly to the requirement for realistic portfolio tasks.
    """
    if Project.query.first() or Task.query.first():
        return  # Data already exists, do not duplicate

    # Create realistic sample projects
    projects_data = [
        {
            "name": "Website Redesign",
            "description": "Overhaul landing page, customer dashboard, and mobile responsive navigation for TaskFlow SaaS.",
            "status": "ACTIVE",
            "deadline": date.today() + timedelta(days=14)
        },
        {
            "name": "Python Learning",
            "description": "Master advanced collection operations, object relational mapping, and full-stack Flask architecture.",
            "status": "ACTIVE",
            "deadline": date.today() + timedelta(days=30)
        },
        {
            "name": "College Assignment",
            "description": "Comprehensive documentation, test suites, and presentation slides for the semester internship project.",
            "status": "ACTIVE",
            "deadline": date.today() + timedelta(days=7)
        },
        {
            "name": "Personal Productivity",
            "description": "Establish daily deep-work routines, sprint planning, and quarterly personal milestone reviews.",
            "status": "ACTIVE",
            "deadline": date.today() + timedelta(days=45)
        }
    ]

    project_instances = []
    for p in projects_data:
        proj = Project(
            name=p["name"],
            description=p["description"],
            status=p["status"],
            deadline=p["deadline"]
        )
        db.session.add(proj)
        project_instances.append(proj)

    db.session.commit()

    # Create realistic sample tasks
    tasks_data = [
        # Website Redesign
        {
            "title": "Design dashboard wireframe",
            "description": "Create high-fidelity mockups focusing on typography, generous spacing, and calm lavender accents.",
            "status": "COMPLETED",
            "priority": "HIGH",
            "category": "Design",
            "due_date": date.today() - timedelta(days=2),
            "project_id": project_instances[0].id
        },
        {
            "title": "Test responsive layout",
            "description": "Verify fluid card stacking on mobile viewports and ensure sidebar collapses cleanly on tablet breakpoints.",
            "status": "IN_PROGRESS",
            "priority": "HIGH",
            "category": "Testing",
            "due_date": date.today() + timedelta(days=3),
            "project_id": project_instances[0].id
        },
        {
            "title": "Implement dark mode theme toggle",
            "description": "Define CSS custom properties for surfaces, borders, and contrast ratios with localStorage persistence.",
            "status": "COMPLETED",
            "priority": "MEDIUM",
            "category": "Development",
            "due_date": date.today() - timedelta(days=1),
            "project_id": project_instances[0].id
        },
        # Python Learning
        {
            "title": "Review database schema",
            "description": "Inspect foreign keys, cascade delete rules, and datetime constraints for Project and Task tables.",
            "status": "COMPLETED",
            "priority": "HIGH",
            "category": "Development",
            "due_date": date.today() - timedelta(days=4),
            "project_id": project_instances[1].id
        },
        {
            "title": "Complete Flask API integration",
            "description": "Implement RESTful JSON endpoints for dynamic Chart.js chart synchronization and task status toggles.",
            "status": "IN_PROGRESS",
            "priority": "URGENT",
            "category": "Development",
            "due_date": date.today() + timedelta(days=2),
            "project_id": project_instances[1].id
        },
        {
            "title": "Refactor collection operations into services layer",
            "description": "Explicitly implement list.append(), loops, and dictionary transformations for educational clarity.",
            "status": "COMPLETED",
            "priority": "MEDIUM",
            "category": "Development",
            "due_date": date.today() - timedelta(days=1),
            "project_id": project_instances[1].id
        },
        # College Assignment
        {
            "title": "Finalize Python project documentation",
            "description": "Draft comprehensive README including architecture diagrams, Input-Process-Output flow, and installation guide.",
            "status": "IN_PROGRESS",
            "priority": "URGENT",
            "category": "Documentation",
            "due_date": date.today() + timedelta(days=1),
            "project_id": project_instances[2].id
        },
        {
            "title": "Prepare project presentation",
            "description": "Compile slide deck illustrating technical evolution from volatile console to persistent web dashboard.",
            "status": "TODO",
            "priority": "HIGH",
            "category": "Planning",
            "due_date": date.today() + timedelta(days=5),
            "project_id": project_instances[2].id
        },
        {
            "title": "Execute comprehensive pytest test suite",
            "description": "Write automated test cases verifying CRUD operations, edge-case validations, and metric division by zero.",
            "status": "TODO",
            "priority": "MEDIUM",
            "category": "Testing",
            "due_date": date.today() + timedelta(days=4),
            "project_id": project_instances[2].id
        },
        # Personal Productivity
        {
            "title": "Audit weekly time allocation",
            "description": "Evaluate time distribution between feature coding, automated testing, and code review routines.",
            "status": "TODO",
            "priority": "LOW",
            "category": "Research",
            "due_date": date.today() + timedelta(days=8),
            "project_id": project_instances[3].id
        },
        {
            "title": "Setup Git repository and branch protection",
            "description": "Verify .gitignore rules for virtual environments, initialize main branch, and prepare GitHub push scripts.",
            "status": "COMPLETED",
            "priority": "MEDIUM",
            "category": "Development",
            "due_date": date.today() - timedelta(days=3),
            "project_id": project_instances[3].id
        },
        {
            "title": "Conduct past-deadline task review",
            "description": "Identify root causes for overdue deliverables and recalibrate sprint velocity estimates.",
            "status": "TODO",
            "priority": "HIGH",
            "category": "Planning",
            "due_date": date.today() - timedelta(days=2),  # Intentionally overdue for testing
            "project_id": project_instances[3].id
        }
    ]

    for t in tasks_data:
        task = Task(
            title=t["title"],
            description=t["description"],
            status=t["status"],
            priority=t["priority"],
            category=t["category"],
            due_date=t["due_date"],
            project_id=t["project_id"]
        )
        db.session.add(task)

    db.session.commit()
