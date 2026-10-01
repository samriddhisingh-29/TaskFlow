/**
 * TaskFlow — Core Application JavaScript
 * Manages Dark Mode, Mobile Sidebar, Toast Notifications, and Global Modals.
 */

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initMobileSidebar();
  initModals();
  initAutoDismissFlashes();
});

/**
 * 1. Dark Mode System with localStorage Persistence
 */
function initTheme() {
  const themeToggleBtn = document.getElementById("themeToggleBtn");
  const themeIcon = document.getElementById("themeIcon");
  const themeLabel = document.getElementById("themeLabel");

  const savedTheme = localStorage.getItem("taskflow-theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateThemeUI(savedTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
      const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
      const newTheme = currentTheme === "dark" ? "light" : "dark";
      
      document.documentElement.setAttribute("data-theme", newTheme);
      localStorage.setItem("taskflow-theme", newTheme);
      updateThemeUI(newTheme);

      // Trigger custom event so Chart.js can re-theme if present
      window.dispatchEvent(new CustomEvent("themeChanged", { detail: { theme: newTheme } }));
    });
  }

  function updateThemeUI(theme) {
    if (themeIcon) {
      themeIcon.textContent = theme === "dark" ? "☀️" : "🌙";
    }
    if (themeLabel) {
      themeLabel.textContent = theme === "dark" ? "Light Mode" : "Dark Mode";
    }
  }
}

/**
 * 2. Mobile Responsive Sidebar Navigation
 */
function initMobileSidebar() {
  const menuToggle = document.getElementById("mobileMenuToggle");
  const sidebar = document.querySelector(".app-sidebar");

  if (menuToggle && sidebar) {
    menuToggle.addEventListener("click", (e) => {
      e.stopPropagation();
      sidebar.classList.toggle("open");
    });

    document.addEventListener("click", (e) => {
      if (sidebar.classList.contains("open") && !sidebar.contains(e.target) && e.target !== menuToggle) {
        sidebar.classList.remove("open");
      }
    });
  }
}

/**
 * 3. Modal Dialog System
 */
function initModals() {
  // Modal Triggers via data-modal-target
  document.querySelectorAll("[data-modal-target]").forEach((trigger) => {
    trigger.addEventListener("click", (e) => {
      e.preventDefault();
      const modalId = trigger.getAttribute("data-modal-target");
      openModal(modalId);
    });
  });

  // Close buttons inside modals
  document.querySelectorAll(".modal-close-btn, [data-modal-close]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const modal = btn.closest(".modal-backdrop");
      if (modal) {
        closeModal(modal.id);
      }
    });
  });

  // Click outside modal content to close
  document.querySelectorAll(".modal-backdrop").forEach((backdrop) => {
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) {
        closeModal(backdrop.id);
      }
    });
  });

  // ESC key to close
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal-backdrop.show").forEach((modal) => {
        closeModal(modal.id);
      });
    }
  });
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add("show");
    document.body.style.overflow = "hidden";
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove("show");
    document.body.style.overflow = "";
  }
}

/**
 * 4. Toast Notification Utility
 */
function showToast(message, type = "success") {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  
  let icon = "✓";
  if (type === "danger") icon = "✕";
  if (type === "info") icon = "ℹ";

  toast.innerHTML = `
    <span style="font-weight: bold;">${icon}</span>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

/**
 * 5. Auto-dismiss Server Flash Messages
 */
function initAutoDismissFlashes() {
  document.querySelectorAll(".flash-message").forEach((flash) => {
    setTimeout(() => {
      flash.style.opacity = "0";
      flash.style.transition = "opacity 0.4s ease";
      setTimeout(() => flash.remove(), 400);
    }, 4500);
  });
}
