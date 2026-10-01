/**
 * TaskFlow — Task Interaction Handlers
 * Manages quick status toggling, modal prefilling, and task mutations.
 */

document.addEventListener("DOMContentLoaded", () => {
  initStatusToggles();
  initEditTaskButtons();
  initDeleteTaskButtons();
});

/**
 * 1. Quick Task Status Toggle via Asynchronous Fetch
 */
function initStatusToggles() {
  document.querySelectorAll(".task-toggle-btn").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      const taskId = btn.getAttribute("data-task-id");
      if (!taskId) return;

      try {
        const response = await fetch(`/tasks/${taskId}/toggle`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/json"
          }
        });

        const result = await response.json();

        if (response.ok && result.success) {
          showToast(result.message || "Task updated", "success");

          // Update UI row or card
          const row = btn.closest("tr") || btn.closest(".task-card-item");
          if (row) {
            const isCompleted = result.task.status === "COMPLETED";
            const titleEl = row.querySelector(".task-title-text");
            const checkboxEl = row.querySelector(".task-checkbox-btn");

            if (checkboxEl) {
              if (isCompleted) {
                checkboxEl.classList.add("checked");
                checkboxEl.textContent = "✓";
              } else {
                checkboxEl.classList.remove("checked");
                checkboxEl.textContent = "";
              }
            }

            if (titleEl) {
              if (isCompleted) {
                titleEl.classList.add("completed");
              } else {
                titleEl.classList.remove("completed");
              }
            }
          }

          // If on dashboard, reload after brief moment to reflect recalculated metrics
          if (window.location.pathname === "/" || window.location.pathname === "/reports") {
            setTimeout(() => window.location.reload(), 600);
          }
        } else {
          showToast(result.error || "Failed to update task", "danger");
        }
      } catch (err) {
        console.error("Toggle error:", err);
        showToast("Network error updating task status", "danger");
      }
    });
  });
}

/**
 * 2. Edit Task Modal Prefilling
 */
function initEditTaskButtons() {
  document.querySelectorAll(".edit-task-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const taskId = btn.getAttribute("data-id");
      const title = btn.getAttribute("data-title");
      const description = btn.getAttribute("data-desc");
      const status = btn.getAttribute("data-status");
      const priority = btn.getAttribute("data-priority");
      const category = btn.getAttribute("data-category");
      const dueDate = btn.getAttribute("data-due");
      const projectId = btn.getAttribute("data-project");

      const form = document.getElementById("editTaskForm");
      if (form) {
        form.action = `/tasks/${taskId}/edit`;
        document.getElementById("edit_task_id").value = taskId || "";
        document.getElementById("edit_title").value = title || "";
        document.getElementById("edit_description").value = description || "";
        document.getElementById("edit_status").value = status || "TODO";
        document.getElementById("edit_priority").value = priority || "MEDIUM";
        document.getElementById("edit_category").value = category || "General";
        document.getElementById("edit_due_date").value = dueDate || "";
        document.getElementById("edit_project_id").value = projectId || "";

        openModal("editTaskModal");
      }
    });
  });
}

/**
 * 3. Delete Task Confirmation Modal
 */
function initDeleteTaskButtons() {
  document.querySelectorAll(".delete-task-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const taskId = btn.getAttribute("data-id");
      const taskTitle = btn.getAttribute("data-title");

      const form = document.getElementById("deleteTaskForm");
      const titleTarget = document.getElementById("deleteTaskTitle");

      if (form) {
        form.action = `/tasks/${taskId}/delete`;
        if (titleTarget) {
          titleTarget.textContent = taskTitle || "this task";
        }
        openModal("deleteTaskModal");
      }
    });
  });
}
