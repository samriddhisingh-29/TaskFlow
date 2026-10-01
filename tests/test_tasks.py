from datetime import date, timedelta
from app.models import db, Task
from app.services import (
    create_task,
    update_task,
    toggle_task_status,
    delete_task,
    validate_task_data,
    filter_and_sort_tasks,
    get_all_tasks_as_list
)

def test_validate_task_data_valid(app):
    """Test validation succeeds with correct task parameters."""
    with app.app_context():
        valid_payload = {
            "title": "Develop Unit Tests",
            "description": "Ensure high coverage across CRUD routes",
            "status": "TODO",
            "priority": "HIGH",
            "category": "Testing",
            "due_date": str(date.today() + timedelta(days=2))
        }
        is_valid, cleaned = validate_task_data(valid_payload)
        assert is_valid is True
        assert cleaned["title"] == "Develop Unit Tests"
        assert cleaned["priority"] == "HIGH"
        assert cleaned["status"] == "TODO"

def test_validate_task_data_invalid(app):
    """Test validation catches missing or invalid data."""
    with app.app_context():
        # Title too short (< 3 characters)
        is_valid, err = validate_task_data({"title": "ab"})
        assert is_valid is False
        assert "at least 3 characters" in err

        # Missing title
        is_valid, err = validate_task_data({"title": ""})
        assert is_valid is False
        assert "required" in err

        # Invalid status
        is_valid, err = validate_task_data({"title": "Valid Title", "status": "UNKNOWN_STATUS"})
        assert is_valid is False
        assert "Invalid status" in err

        # Invalid priority
        is_valid, err = validate_task_data({"title": "Valid Title", "priority": "CRITICAL"})
        assert is_valid is False
        assert "Invalid priority" in err

def test_create_task(app, sample_project):
    """Test creating a new task persists to database."""
    with app.app_context():
        task, error = create_task({
            "title": "Build Integration Pipeline",
            "description": "Configure CI runner for pytest",
            "status": "IN_PROGRESS",
            "priority": "URGENT",
            "category": "DevOps",
            "project_id": sample_project.id
        })
        assert error is None
        assert task is not None
        assert task.id is not None
        assert task.title == "Build Integration Pipeline"
        assert task.project_id == sample_project.id

        # Verify query
        saved = db.session.get(Task, task.id)
        assert saved is not None
        assert saved.category == "DevOps"

def test_toggle_task_status(app, sample_task):
    """Test toggling status from TODO to COMPLETED and back."""
    with app.app_context():
        # Initial status is TODO
        assert sample_task.status == "TODO"

        # Toggle to COMPLETED
        updated, error = toggle_task_status(sample_task.id)
        assert error is None
        assert updated.status == "COMPLETED"

        # Toggle back to TODO
        updated_again, error = toggle_task_status(sample_task.id)
        assert error is None
        assert updated_again.status == "TODO"

def test_update_task(app, sample_task):
    """Test editing task attributes."""
    with app.app_context():
        updated, error = update_task(sample_task.id, {
            "title": "Renamed Test Task",
            "description": "Updated description content",
            "status": "IN_PROGRESS",
            "priority": "LOW",
            "category": "Documentation"
        })
        assert error is None
        assert updated.title == "Renamed Test Task"
        assert updated.status == "IN_PROGRESS"
        assert updated.priority == "LOW"

def test_delete_task(app, sample_task):
    """Test removing a task removes it from database."""
    with app.app_context():
        task_id = sample_task.id
        success, error = delete_task(task_id)
        assert success is True
        assert error is None
        assert db.session.get(Task, task_id) is None

def test_filter_and_sort_tasks():
    """Test collection filtering and sorting logic in services."""
    raw_tasks = [
        {"id": 1, "title": "Write documentation", "description": "Docs", "status": "TODO", "priority": "LOW", "category": "Docs", "project_name": "Project A", "due_date": "2026-10-05"},
        {"id": 2, "title": "Fix security vulnerability", "description": "Auth bug", "status": "IN_PROGRESS", "priority": "URGENT", "category": "Security", "project_name": "Project B", "due_date": "2026-10-01"},
        {"id": 3, "title": "Deploy to staging", "description": "Release", "status": "COMPLETED", "priority": "HIGH", "category": "DevOps", "project_name": "Project A", "due_date": "2026-10-02"}
    ]

    # Filter by status
    completed_only = filter_and_sort_tasks(raw_tasks, status_filter="COMPLETED")
    assert len(completed_only) == 1
    assert completed_only[0]["id"] == 3

    # Filter by priority
    urgent_only = filter_and_sort_tasks(raw_tasks, priority_filter="URGENT")
    assert len(urgent_only) == 1
    assert urgent_only[0]["id"] == 2

    # Filter by search query (matching description)
    matched = filter_and_sort_tasks(raw_tasks, search_query="bug")
    assert len(matched) == 1
    assert matched[0]["id"] == 2

    # Sort by priority desc (URGENT > HIGH > LOW)
    sorted_by_priority = filter_and_sort_tasks(raw_tasks, sort_by="priority_desc")
    assert sorted_by_priority[0]["priority"] == "URGENT"
    assert sorted_by_priority[1]["priority"] == "HIGH"
    assert sorted_by_priority[2]["priority"] == "LOW"
