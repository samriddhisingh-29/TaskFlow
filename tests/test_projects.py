from datetime import date, timedelta
from app.models import db, Project, Task
from app.services import (
    create_project,
    validate_project_data,
    get_project_details
)

def test_validate_project_data(app):
    """Test project validation rules."""
    with app.app_context():
        # Valid
        is_valid, cleaned = validate_project_data({
            "name": "Frontend Overhaul",
            "description": "Revamp design",
            "status": "ACTIVE",
            "deadline": str(date.today() + timedelta(days=20))
        })
        assert is_valid is True
        assert cleaned["name"] == "Frontend Overhaul"

        # Missing name
        is_valid, err = validate_project_data({"name": ""})
        assert is_valid is False
        assert "required" in err

        # Name too short
        is_valid, err = validate_project_data({"name": "A"})
        assert is_valid is False
        assert "at least 2 characters" in err

        # Invalid status
        is_valid, err = validate_project_data({"name": "Valid Name", "status": "UNKNOWN"})
        assert is_valid is False
        assert "Invalid project status" in err

def test_create_project(app):
    """Test creating and persisting a new project."""
    with app.app_context():
        project, error = create_project({
            "name": "Backend Refactoring",
            "description": "Clean modular services architecture",
            "status": "ACTIVE"
        })
        assert error is None
        assert project is not None
        assert project.id is not None
        assert project.name == "Backend Refactoring"

def test_get_project_details(app, sample_project):
    """Test project task count and percentage calculations."""
    with app.app_context():
        # Add 1 completed and 1 todo task
        t1 = Task(
            title="Task 1",
            status="COMPLETED",
            priority="HIGH",
            project_id=sample_project.id
        )
        t2 = Task(
            title="Task 2",
            status="TODO",
            priority="MEDIUM",
            project_id=sample_project.id
        )
        db.session.add_all([t1, t2])
        db.session.commit()

        details = get_project_details(sample_project.id)
        assert details is not None
        assert details["total_tasks"] == 2
        assert details["completed_tasks"] == 1
        assert details["pending_tasks"] == 1
        assert details["progress_percentage"] == 50.0

def test_project_cascade_delete(app, sample_project):
    """Test deleting a project also removes its associated tasks."""
    with app.app_context():
        project = db.session.get(Project, sample_project.id)
        task = Task(
            title="Dependent Task",
            project_id=project.id
        )
        db.session.add(task)
        db.session.commit()
        task_id = task.id

        # Delete project
        db.session.delete(project)
        db.session.commit()

        # Task should be deleted by cascade
        assert db.session.get(Task, task_id) is None
