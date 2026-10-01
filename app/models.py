from datetime import datetime, date, timezone
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Allowed constants for validation and filtering
VALID_PRIORITIES = ["LOW", "MEDIUM", "HIGH", "URGENT"]
VALID_TASK_STATUSES = ["TODO", "IN_PROGRESS", "COMPLETED"]
VALID_PROJECT_STATUSES = ["ACTIVE", "COMPLETED", "ON_HOLD"]
DEFAULT_CATEGORIES = ["Development", "Design", "Documentation", "Testing", "Research", "General"]

def get_current_time():
    """Returns timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)

class Project(db.Model):
    """
    Project model representing a high-level initiative containing multiple tasks.
    Demonstrates one-to-many relationship with Task.
    """
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="ACTIVE", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=get_current_time, nullable=False)
    deadline = db.Column(db.Date, nullable=True)

    # Relationship to tasks: when a project is deleted, its tasks are cascade removed
    tasks = db.relationship(
        "Task",
        backref="project",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="Task.created_at.desc()"
    )

    def to_dict(self):
        """Converts model instance to a standard Python dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description or "",
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None,
            "deadline": self.deadline.strftime("%Y-%m-%d") if self.deadline else None,
            "task_count": len(self.tasks)
        }

    def __repr__(self):
        return f"<Project {self.id}: {self.name}>"


class Task(db.Model):
    """
    Task model representing an actionable item.
    Enforces status, priority, and relationship to Project.
    """
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="TODO", nullable=False)
    priority = db.Column(db.String(20), default="MEDIUM", nullable=False)
    category = db.Column(db.String(50), default="General", nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=get_current_time, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=get_current_time, onupdate=get_current_time, nullable=False)

    # Foreign key to Project
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=True)

    @property
    def is_overdue(self):
        """Check if task is past its due date and not completed."""
        if self.status != "COMPLETED" and self.due_date:
            return self.due_date < date.today()
        return False

    def to_dict(self):
        """
        Converts the database record into a clean Python dictionary.
        Demonstrates basic data structure transformation.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description or "",
            "status": self.status,
            "priority": self.priority,
            "category": self.category,
            "due_date": self.due_date.strftime("%Y-%m-%d") if self.due_date else None,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M") if self.updated_at else None,
            "project_id": self.project_id,
            "project_name": self.project.name if self.project else "No Project",
            "is_overdue": self.is_overdue
        }

    def __repr__(self):
        return f"<Task {self.id}: {self.title}>"
