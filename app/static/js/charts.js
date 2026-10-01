/**
 * TaskFlow — Dynamic Chart.js Analytics Engine
 * Fetches JSON metrics asynchronously from /api/analytics and renders dynamic visualizations.
 * Zero hardcoded chart numbers.
 */

document.addEventListener("DOMContentLoaded", () => {
  initCharts();

  // Listen for theme toggle to adjust chart grid colors
  window.addEventListener("themeChanged", () => {
    initCharts();
  });
});

let weeklyChartInstance = null;
let statusChartInstance = null;
let priorityChartInstance = null;
let projectChartInstance = null;

async function initCharts() {
  try {
    const response = await fetch("/api/analytics");
    if (!response.ok) return;

    const data = await response.json();
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";

    const textColor = isDark ? "#cbd5e1" : "#475569";
    const gridColor = isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.05)";

    // Set Chart.js Defaults
    Chart.defaults.color = textColor;
    Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";

    // 1. Weekly Tasks Trend Chart (Dashboard & Reports)
    const weeklyCanvas = document.getElementById("weeklyTrendChart");
    if (weeklyCanvas) {
      if (weeklyChartInstance) weeklyChartInstance.destroy();

      weeklyChartInstance = new Chart(weeklyCanvas, {
        type: "bar",
        data: {
          labels: data.weekly_trend.labels,
          datasets: [
            {
              label: "Created",
              data: data.weekly_trend.created,
              backgroundColor: "rgba(124, 58, 237, 0.75)",
              borderRadius: 6,
              barPercentage: 0.6
            },
            {
              label: "Completed",
              data: data.weekly_trend.completed,
              backgroundColor: "rgba(16, 185, 129, 0.75)",
              borderRadius: 6,
              barPercentage: 0.6
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: "top",
              labels: { boxWidth: 12, padding: 16 }
            }
          },
          scales: {
            x: {
              grid: { display: false }
            },
            y: {
              beginAtZero: true,
              ticks: { stepSize: 1 },
              grid: { color: gridColor }
            }
          }
        }
      });
    }

    // 2. Task Status Doughnut Chart (Dashboard & Reports)
    const statusCanvas = document.getElementById("statusDoughnutChart");
    if (statusCanvas) {
      if (statusChartInstance) statusChartInstance.destroy();

      const st = data.status_distribution;
      statusChartInstance = new Chart(statusCanvas, {
        type: "doughnut",
        data: {
          labels: ["Completed", "In Progress", "To-Do"],
          datasets: [
            {
              data: [st.COMPLETED || 0, st.IN_PROGRESS || 0, st.TODO || 0],
              backgroundColor: [
                "#10b981", // Success green
                "#f59e0b", // Amber warning
                "#94a3b8"  // Muted gray
              ],
              borderWidth: 2,
              borderColor: isDark ? "#1e293b" : "#ffffff",
              hoverOffset: 4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: "72%",
          plugins: {
            legend: {
              position: "bottom",
              labels: { boxWidth: 12, padding: 14 }
            }
          }
        }
      });
    }

    // 3. Priority Distribution Horizontal Bar (Reports Page)
    const priorityCanvas = document.getElementById("priorityDistChart");
    if (priorityCanvas) {
      if (priorityChartInstance) priorityChartInstance.destroy();

      const pr = data.priority_distribution;
      priorityChartInstance = new Chart(priorityCanvas, {
        type: "bar",
        data: {
          labels: ["Urgent", "High", "Medium", "Low"],
          datasets: [
            {
              label: "Tasks by Priority",
              data: [pr.URGENT || 0, pr.HIGH || 0, pr.MEDIUM || 0, pr.LOW || 0],
              backgroundColor: ["#ef4444", "#f59e0b", "#0284c7", "#64748b"],
              borderRadius: 6
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: "y",
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              beginAtZero: true,
              ticks: { stepSize: 1 },
              grid: { color: gridColor }
            },
            y: {
              grid: { display: false }
            }
          }
        }
      });
    }

    // 4. Project Progress Horizontal Bar (Reports Page)
    const projectCanvas = document.getElementById("projectProgressChart");
    if (projectCanvas && data.project_progress && data.project_progress.length > 0) {
      if (projectChartInstance) projectChartInstance.destroy();

      const projNames = data.project_progress.map(p => p.name);
      const projPercentages = data.project_progress.map(p => p.progress_percentage);

      projectChartInstance = new Chart(projectCanvas, {
        type: "bar",
        data: {
          labels: projNames,
          datasets: [
            {
              label: "Completion %",
              data: projPercentages,
              backgroundColor: "rgba(124, 58, 237, 0.8)",
              borderRadius: 6
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: "y",
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              beginAtZero: true,
              max: 100,
              ticks: {
                callback: (val) => val + "%"
              },
              grid: { color: gridColor }
            },
            y: {
              grid: { display: false }
            }
          }
        }
      });
    }

  } catch (error) {
    console.error("Error loading analytics data:", error);
  }
}
