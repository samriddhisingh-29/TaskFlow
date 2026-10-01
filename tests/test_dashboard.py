from datetime import date, timedelta
from app.models import db, Task, Project
from app.services import calculate_dashboard_metrics, get_analytics_data

def test_dashboard_calculations_empty(app):
    """Test dashboard calculations when no tasks exist (safe division by zero)."""
    with app.app_context():
        metrics = calculate_dashboard_metrics([])
        assert metrics["total_tasks"] == 0
        assert metrics["completed_tasks"] == 0
        assert metrics["pending_tasks"] == 0
        assert metrics["overdue_tasks"] == 0
        assert metrics["completion_percentage"] == 0.0

def test_dashboard_calculations_populated(app):
    """Test math aggregations across multiple task states."""
    test_collection = [
        {"id": 1, "status": "COMPLETED", "is_overdue": False},
        {"id": 2, "status": "COMPLETED", "is_overdue": False},
        {"id": 3, "status": "IN_PROGRESS", "is_overdue": False},
        {"id": 4, "status": "TODO", "is_overdue": True},  # 1 overdue
    ]

    metrics = calculate_dashboard_metrics(test_collection)
    assert metrics["total_tasks"] == 4
    assert metrics["completed_tasks"] == 2
    assert metrics["in_progress_tasks"] == 1
    assert metrics["todo_tasks"] == 1
    assert metrics["pending_tasks"] == 2
    assert metrics["overdue_tasks"] == 1
    assert metrics["completion_percentage"] == 50.0

def test_api_analytics_endpoint(client, sample_task):
    """Test /api/analytics returns structured JSON for Chart.js."""
    response = client.get("/api/analytics")
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()

    assert "status_distribution" in data
    assert "priority_distribution" in data
    assert "category_distribution" in data
    assert "weekly_trend" in data
    assert "project_progress" in data
    assert data["status_distribution"]["TODO"] >= 1

def test_export_csv_endpoint(client, sample_task):
    """Test /tasks/export generates valid dynamic CSV data."""
    response = client.get("/tasks/export")
    assert response.status_code == 200
    assert "text/csv" in response.content_type
    assert "attachment;filename=" in response.headers["Content-Disposition"]

    content = response.data.decode("utf-8")
    # Verify header columns
    assert "Task ID,Title,Description,Status,Priority,Category,Project,Due Date,Is Overdue" in content
    # Verify sample task row
    assert sample_task.title in content
