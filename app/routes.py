"""
TaskFlow Application Routes
===========================
Architecture: INPUT -> PROCESS -> OUTPUT
Handles routing, user input extraction, service delegation, and response rendering.
"""

import csv
import io
from datetime import date
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, jsonify, Response, abort
)
from app.models import Project, Task, VALID_PRIORITIES, VALID_TASK_STATUSES, DEFAULT_CATEGORIES
from app.services import (
    get_all_tasks_as_list,
    filter_and_sort_tasks,
    calculate_dashboard_metrics,
    get_analytics_data,
    create_task,
    update_task,
    toggle_task_status,
    delete_task,
    create_project,
    get_project_details
)

main_bp = Blueprint("main", __name__)


# ==============================================================================
# 1. DASHBOARD ROUTE
# ==============================================================================

@main_bp.route("/")
def dashboard():
    """
    Renders the primary dashboard with calculated metrics, dynamic charts,
    recent tasks, and upcoming deadlines.
    """
    # PROCESS: Fetch all tasks transformed into Python dictionaries
    tasks = get_all_tasks_as_list()
    projects = Project.query.order_by(Project.created_at.desc()).all()

    # Calculate real-time dashboard metrics (no hardcoded figures)
    metrics = calculate_dashboard_metrics(tasks)

    # Filter recent tasks (first 5)
    recent_tasks = tasks[:5]

    # Filter upcoming deadlines (tasks with due dates in future or today, not completed)
    upcoming_tasks = [
        t for t in tasks
        if t["due_date"] and t["status"] != "COMPLETED" and not t["is_overdue"]
    ]
    # Sort upcoming by earliest due date
    upcoming_tasks = sorted(upcoming_tasks, key=lambda t: t["due_date"])[:5]

    # Overdue tasks list
    overdue_list = [t for t in tasks if t["is_overdue"]][:5]

    return render_template(
        "dashboard.html",
        metrics=metrics,
        recent_tasks=recent_tasks,
        upcoming_tasks=upcoming_tasks,
        overdue_list=overdue_list,
        projects=projects,
        priorities=VALID_PRIORITIES,
        statuses=VALID_TASK_STATUSES,
        categories=DEFAULT_CATEGORIES
    )


# ==============================================================================
# 2. TASK MANAGEMENT ROUTES (CRUD, Filter, Search, Sort)
# ==============================================================================

@main_bp.route("/tasks")
def tasks():
    """
    Task management interface with multi-field search, filtering, and sorting.
    """
    # INPUT: Query parameters
    search_query = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "ALL")
    priority_filter = request.args.get("priority", "ALL")
    category_filter = request.args.get("category", "ALL")
    sort_by = request.args.get("sort", "created_desc")

    # PROCESS: Retrieve all tasks as list and apply collection filters
    all_tasks = get_all_tasks_as_list()
    filtered_tasks = filter_and_sort_tasks(
        all_tasks,
        search_query=search_query,
        status_filter=status_filter,
        priority_filter=priority_filter,
        category_filter=category_filter,
        sort_by=sort_by
    )

    projects = Project.query.all()

    # Extract distinct categories from tasks for dynamic filter pills
    active_categories = list(set([t["category"] for t in all_tasks] + DEFAULT_CATEGORIES))
    active_categories.sort()

    # OUTPUT: Render tasks template
    return render_template(
        "tasks.html",
        tasks=filtered_tasks,
        total_count=len(all_tasks),
        filtered_count=len(filtered_tasks),
        search_query=search_query,
        current_status=status_filter,
        current_priority=priority_filter,
        current_category=category_filter,
        current_sort=sort_by,
        projects=projects,
        categories=active_categories,
        priorities=VALID_PRIORITIES,
        statuses=VALID_TASK_STATUSES
    )


def wants_json():
    """Detect if client expects a JSON response."""
    return request.is_json or request.headers.get("Accept") == "application/json" or request.headers.get("X-Requested-With") == "XMLHttpRequest"

@main_bp.route("/tasks/create", methods=["POST"])
def add_task():
    """
    INPUT -> PROCESS -> OUTPUT
    Receives form or JSON submission, validates, creates task, returns response.
    """
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    task, error = create_task(data)

    if error:
        if wants_json():
            return jsonify({"success": False, "error": error}), 400
        flash(f"Error creating task: {error}", "danger")
        return redirect(request.referrer or url_for("main.tasks"))

    if wants_json():
        return jsonify({
            "success": True,
            "message": "Task created successfully!",
            "task": task.to_dict()
        }), 201

    flash("Task created successfully!", "success")
    return redirect(request.referrer or url_for("main.tasks"))


@main_bp.route("/tasks/<int:task_id>/edit", methods=["POST"])
def edit_task(task_id):
    """
    Updates an existing task with validated parameters.
    """
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    task, error = update_task(task_id, data)

    if error:
        if wants_json():
            return jsonify({"success": False, "error": error}), 400
        flash(f"Error updating task: {error}", "danger")
        return redirect(request.referrer or url_for("main.tasks"))

    if wants_json():
        return jsonify({
            "success": True,
            "message": "Task updated successfully!",
            "task": task.to_dict()
        }), 200

    flash("Task updated successfully!", "success")
    return redirect(request.referrer or url_for("main.tasks"))


@main_bp.route("/tasks/<int:task_id>/toggle", methods=["POST"])
def toggle_status(task_id):
    """
    Quick status toggle between COMPLETED and TODO/IN_PROGRESS.
    """
    task, error = toggle_task_status(task_id)

    if error:
        if wants_json():
            return jsonify({"success": False, "error": error}), 400
        flash(f"Error updating status: {error}", "danger")
        return redirect(request.referrer or url_for("main.tasks"))

    if wants_json():
        return jsonify({
            "success": True,
            "message": f"Task status updated to {task.status}",
            "task": task.to_dict()
        }), 200

    flash(f"Task marked as {task.status.replace('_', ' ').title()}.", "success")
    return redirect(request.referrer or url_for("main.tasks"))


@main_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
def remove_task(task_id):
    """
    Deletes a task by ID.
    """
    success, error = delete_task(task_id)

    if not success:
        if wants_json():
            return jsonify({"success": False, "error": error}), 404
        flash(f"Error deleting task: {error}", "danger")
        return redirect(request.referrer or url_for("main.tasks"))

    if wants_json():
        return jsonify({
            "success": True,
            "message": "Task deleted successfully!"
        }), 200

    flash("Task removed successfully.", "info")
    return redirect(request.referrer or url_for("main.tasks"))


# ==============================================================================
# 3. PROJECT ROUTES
# ==============================================================================

@main_bp.route("/projects")
def projects():
    """
    Project overview page displaying project cards with task stats and progress rings.
    """
    all_projects = Project.query.order_by(Project.created_at.desc()).all()
    
    # Process project summaries
    project_cards = []
    for proj in all_projects:
        details = get_project_details(proj.id)
        project_cards.append(details)

    return render_template(
        "projects.html",
        projects=project_cards
    )


@main_bp.route("/projects/create", methods=["POST"])
def add_project():
    """Creates a new project record."""
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    project, error = create_project(data)

    if error:
        if wants_json():
            return jsonify({"success": False, "error": error}), 400
        flash(f"Error creating project: {error}", "danger")
        return redirect(url_for("main.projects"))

    if wants_json():
        return jsonify({
            "success": True,
            "message": "Project created successfully!",
            "project": project.to_dict()
        }), 201

    flash("Project created successfully!", "success")
    return redirect(url_for("main.projects"))


@main_bp.route("/projects/<int:project_id>")
def project_detail(project_id):
    """
    Detailed project page with progress ring, task list, and productivity stats.
    """
    details = get_project_details(project_id)
    if not details:
        abort(404)

    return render_template(
        "project_detail.html",
        details=details,
        project=details["project"],
        tasks=details["tasks"],
        priorities=VALID_PRIORITIES,
        statuses=VALID_TASK_STATUSES,
        categories=DEFAULT_CATEGORIES
    )


# ==============================================================================
# 4. ANALYTICS & REPORTS ROUTE
# ==============================================================================

@main_bp.route("/reports")
def reports():
    """
    Analytics report page displaying interactive Chart.js visualizations.
    """
    metrics = calculate_dashboard_metrics()
    analytics_data = get_analytics_data()

    return render_template(
        "reports.html",
        metrics=metrics,
        analytics=analytics_data
    )


@main_bp.route("/api/analytics")
def api_analytics():
    """
    JSON endpoint providing dynamic chart data to Chart.js asynchronously.
    """
    data = get_analytics_data()
    return jsonify(data)


# ==============================================================================
# 5. DYNAMIC CSV EXPORT
# ==============================================================================

@main_bp.route("/tasks/export")
def export_tasks_csv():
    """
    Dynamically generates a CSV file from actual task database records.
    Demonstrates in-memory stream generation and file delivery without external paid libraries.
    """
    tasks = get_all_tasks_as_list()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header Row
    writer.writerow([
        "Task ID",
        "Title",
        "Description",
        "Status",
        "Priority",
        "Category",
        "Project",
        "Due Date",
        "Is Overdue",
        "Created At",
        "Updated At"
    ])

    # Data Rows
    for t in tasks:
        writer.writerow([
            t["id"],
            t["title"],
            t["description"],
            t["status"],
            t["priority"],
            t["category"],
            t["project_name"],
            t["due_date"] or "None",
            "YES" if t["is_overdue"] else "NO",
            t["created_at"] or "",
            t["updated_at"] or ""
        ])

    output.seek(0)
    filename = f"taskflow_tasks_{date.today().strftime('%Y%m%d')}.csv"

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
