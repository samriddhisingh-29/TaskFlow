import pytest
from app import create_app
from app.models import db, Project, Task

@pytest.fixture
def app():
    """Create and configure a clean testing app instance."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client for HTTP requests."""
    return app.test_client()

@pytest.fixture
def sample_project(app):
    """Creates a sample project fixture."""
    project = Project(
        name="Test Project",
        description="A project created for automated test cases."
    )
    db.session.add(project)
    db.session.commit()
    return project

@pytest.fixture
def sample_task(app, sample_project):
    """Creates a sample task fixture."""
    task = Task(
        title="Sample Test Task",
        description="Task for testing verification",
        status="TODO",
        priority="HIGH",
        category="Testing",
        project_id=sample_project.id
    )
    db.session.add(task)
    db.session.commit()
    return task
