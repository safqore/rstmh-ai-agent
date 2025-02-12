document.addEventListener("DOMContentLoaded", () => {
  fetchDashboardData();
  setupEventListeners();
});

function fetchDashboardData() {
  fetch("/dashboard/api/dashboard-data")
    .then((response) => response.json())
    .then((data) => {
      console.log("API Response:", data);
      document.getElementById("total-sessions").innerText =
        data.sessions ?? "Error";
      document.getElementById("total-users").innerText = data.users ?? "Error";
    })
    .catch((error) => {
      console.error("Error fetching dashboard data:", error);
      document.getElementById("total-sessions").innerText = "Error";
      document.getElementById("total-users").innerText = "Error";
    });
}

function setupEventListeners() {
  document
    .getElementById("total-sessions")
    .addEventListener("click", fetchSessions);
}

function fetchSessions() {
  console.log("[DEBUG] Fetching session data...");

  fetch("/dashboard/api/sessions?limit=10&offset=0")
    .then((response) => response.json())
    .then((data) => {
      console.log("[DEBUG] Sessions Data:", data);

      // Check if data is an object and contains 'sessions'
      if (!data || !data.sessions || !Array.isArray(data.sessions)) {
        console.error("[ERROR] Invalid response format:", data);
        return;
      }

      const sessionList = document.getElementById("session-list");
      sessionList.innerHTML = ""; // Clear existing sessions

      data.sessions.forEach((session) => {
        const sessionItem = document.createElement("li");
        sessionItem.innerHTML = `
                    <span class="session-id">${session.session_id}</span> 
                    <button class="view-session" data-session-id="${session.session_id}">View</button>
                `;
        sessionList.appendChild(sessionItem);
      });

      // Add event listeners for "View" buttons
      document.querySelectorAll(".view-session").forEach((button) => {
        button.addEventListener("click", (event) => {
          const sessionId = event.target.getAttribute("data-session-id");
          fetchSessionDetails(sessionId);
        });
      });

      openModal("session-modal");
    })
    .catch((error) => {
      console.error("Error fetching sessions:", error);
    });
}

function fetchSessionDetails(sessionId) {
  if (!sessionId) {
    console.error("Session ID is missing!");
    return;
  }

  console.log(`[DEBUG] Fetching details for session: ${sessionId}`);

  fetch(
    `/dashboard/api/session-details?session_id=${sessionId}&limit=10&offset=0`
  )
    .then((response) => response.json())
    .then((data) => {
      console.log("[DEBUG] Session Details Response:", data);

      // Ensure modal elements exist before updating
      const modal = document.getElementById("details-modal");
      const detailsList = document.getElementById("details-list");

      if (!modal || !detailsList) {
        console.error("[ERROR] Modal or details container not found!");
        return;
      }

      // Clear previous session details
      detailsList.innerHTML = "";

      if (!data.details || data.details.length === 0) {
        detailsList.innerHTML =
          "<tr><td colspan='3'>No questions found for this session.</td></tr>";
      } else {
        data.details.forEach((detail) => {
          const row = document.createElement("tr");
          row.innerHTML = `
                        <td>${detail.prompt || "N/A"}</td>
                        <td>${detail.response || "N/A"}</td>
                        <td>${new Date(detail.timestamp).toLocaleString()}</td>
                    `;
          detailsList.appendChild(row);
        });
      }

      // Show the modal
      modal.style.display = "block";
    })
    .catch((error) => {
      console.error("Error fetching session details:", error);
    });
}

// Close modal event listener
document.getElementById("close-details-modal").addEventListener("click", () => {
  document.getElementById("details-modal").style.display = "none";
});

// Open a modal
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = "block";
  }
}

// Close modals when the close button is clicked
document.querySelectorAll(".close").forEach((button) => {
  button.addEventListener("click", () => {
    button.parentElement.parentElement.style.display = "none";
  });
});

// Close modal when clicking outside
window.onclick = function (event) {
  document.querySelectorAll(".modal").forEach((modal) => {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });
};
