fetch('/dashboard/api/dashboard-data')
    .then(response => {
        console.log('Raw Response:', response);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('API Response:', data);
        document.getElementById('total-sessions').innerText = data.sessions ?? "Error";
        document.getElementById('total-users').innerText = data.users ?? "Error";
    })
    .catch(error => {
        console.error('Error fetching dashboard data:', error);
        document.getElementById('total-sessions').innerText = "Error";
        document.getElementById('total-users').innerText = "Error";
    });

document.getElementById('total-sessions').addEventListener('click', () => {
    fetch('/dashboard/api/session-details')
        .then(response => response.json())
        .then(data => {
            const modal = document.getElementById('session-modal');
            const list = document.getElementById('session-details-list');
            list.innerHTML = ""; // Clear previous details
            
            if (data.error) {
                list.innerHTML = `<li>${data.error}</li>`;
            } else {
                data.forEach(session => {
                    const item = document.createElement('li');
                    item.textContent = `Session ID: ${session.session_id}, Question: ${session.prompt}, Answer: ${session.response}, Timestamp: ${session.timestamp}`;
                    list.appendChild(item);
                });
            }

            modal.style.display = "block";
        })
        .catch(error => {
            console.error("Error fetching session details:", error);
        });
});

// Modal Elements
const modal = document.getElementById("session-details-modal");
const closeModal = document.getElementById("close-modal");

let currentSessionId = null; // To track the currently opened session
let currentOffset = 0;
const limit = 10;
let filters = {};

// Open the modal
function openModal(sessionId) {
    currentSessionId = sessionId;
    modal.style.display = "block";
    currentOffset = 0; // Reset pagination
    fetchSessionDetails(sessionId, currentOffset, filters);
}

// Close the modal
closeModal.onclick = () => {
    modal.style.display = "none";
};

// Handle filters and fetch new results
document.getElementById("apply-filters").onclick = () => {
    filters = {
        start_date: document.getElementById("filter-start-date").value,
        end_date: document.getElementById("filter-end-date").value,
        user_id: document.getElementById("filter-user-id").value,
        search_query: document.getElementById("search-query").value,
    };
    currentOffset = 0;
    fetchSessionDetails(currentSessionId, currentOffset, filters);
};

// Fetch session details
function fetchSessionDetails(sessionId, offset = 0, filters = {}) {
    if (!sessionId) {
        console.error("Session ID is missing!");
        return;
    }

    const params = new URLSearchParams({
        session_id: sessionId,
        limit,
        offset,
        ...filters,
    });

    fetch(`/dashboard/api/session-details?${params}`)
        .then(response => response.json())
        .then(data => {
            renderSessionDetails(data.details);
            updatePaginationControls(data.total_count, offset / limit);
        })
        .catch(error => {
            console.error("Error fetching session details:", error);
        });
}

// Render session details in the modal
function renderSessionDetails(details) {
    const tableBody = document.getElementById("details-table-body");
    tableBody.innerHTML = ""; // Clear previous results

    details.forEach(detail => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${detail.question || "N/A"}</td>
            <td>${detail.answer || "N/A"}</td>
            <td>${detail.date || "N/A"}</td>
        `;
        tableBody.appendChild(row);
    });
}

// Update pagination controls
function updatePaginationControls(totalCount, currentPage) {
    const totalPages = Math.ceil(totalCount / limit);
    const paginationContainer = document.getElementById("pagination-controls");
    paginationContainer.innerHTML = ""; // Clear existing controls

    for (let i = 0; i < totalPages; i++) {
        const pageButton = document.createElement("button");
        pageButton.textContent = i + 1;
        pageButton.className = i === currentPage ? "active" : "";
        pageButton.onclick = () => {
            currentOffset = i * limit;
            fetchSessionDetails(currentSessionId, currentOffset, filters);
        };
        paginationContainer.appendChild(pageButton);
    }
}

// Close modal on outside click
window.onclick = event => {
    if (event.target === modal) {
        modal.style.display = "none";
    }
};

document.getElementById("total-sessions").addEventListener("click", () => {
    fetch("/dashboard/api/all-sessions")
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            const sessionList = document.getElementById("session-list");
            sessionList.innerHTML = ""; // Clear previous data

            data.sessions.forEach((session) => {
                const item = document.createElement("li");
                item.className = "clickable"; // Add the clickable class
                item.textContent = `Session ID: ${session.session_id}, Total Questions: ${session.question_count}`;
    
                item.innerHTML = `
                    <strong>Session ID:</strong> ${session.session_id} <br>
                    <strong>User ID:</strong> ${session.user_id} <br>
                    <strong>Sample Question:</strong> ${session.sample_prompt || "N/A"} <br>
                    <strong>Timestamp:</strong> ${session.timestamp}
                    <button onclick="fetchSessionDetails('${session.session_id}')">View Details</button>
                `;
                item.onclick = () => {
                    openDetailsModal(session.session_id);
                };
                sessionList.appendChild(item);
            });

            document.getElementById("session-modal").style.display = "block";
        })
        .catch((error) => {
            console.error("Error fetching all sessions:", error);
        });
});

function fetchSessionDetails(sessionId, offset = 0) {
    if (!sessionId) {
        console.error("Session ID is missing!");
        return;
    }

    const params = new URLSearchParams({
        session_id: sessionId,
        limit: 10,
        offset: offset,
    });

    fetch(`/dashboard/api/session-details?${params}`)
        .then((response) => response.json())
        .then((data) => {
            const detailsList = document.getElementById("details-list");
            detailsList.innerHTML = ""; // Clear previous details

            data.details.forEach((detail) => {
                const item = document.createElement("tr");
                item.innerHTML = `
                    <td>${detail.prompt}</td>
                    <td>${detail.response}</td>
                    <td>${detail.timestamp}</td>
                `;
                detailsList.appendChild(item);
            });

            document.getElementById("details-modal").style.display = "block";
        })
        .catch((error) => {
            console.error("Error fetching session details:", error);
        });
}

// Get references to modal close buttons and modals
const sessionModal = document.getElementById("session-modal");
const detailsModal = document.getElementById("details-modal");

const closeSessionModal = document.getElementById("close-session-modal");
const closeDetailsModal = document.getElementById("close-details-modal");

// Close the session modal
closeSessionModal.onclick = () => {
    sessionModal.style.display = "none";
};

// Close the details modal
closeDetailsModal.onclick = () => {
    detailsModal.style.display = "none";
};

// Close modals when clicking outside of them
window.onclick = (event) => {
    if (event.target === sessionModal) {
        sessionModal.style.display = "none";
    }
    if (event.target === detailsModal) {
        detailsModal.style.display = "none";
    }
};

// Render session list in the modal
function renderSessionList(sessions) {
    const sessionList = document.getElementById("session-list");
    sessionList.innerHTML = ""; // Clear existing sessions

    sessions.forEach((session) => {
        const item = document.createElement("li");
        item.textContent = `Session ID: ${session.session_id}, Total Questions: ${session.question_count}`;
        item.onclick = () => {
            openDetailsModal(session.session_id);
        };
        sessionList.appendChild(item);
    });
}

// Open the "Details" modal for a specific session
function openDetailsModal(sessionId) {
    currentSessionId = sessionId;
    detailsModal.style.display = "block";
    currentOffset = 0; // Reset pagination
    fetchSessionDetails(sessionId, currentOffset, filters);
}

// Apply filters and fetch sessions
document.getElementById("apply-session-filters").onclick = () => {
    const searchQuery = document.getElementById("search-query").value;
    fetchSessions({ search_query: searchQuery });
};

// Fetch sessions with optional filters
function fetchSessions(filters = {}) {
    const params = new URLSearchParams({
        limit,
        offset: currentOffset,
        ...filters,
    });

    fetch(`/dashboard/api/sessions?${params}`)
        .then((response) => response.json())
        .then((data) => {
            renderSessionList(data.sessions);
            updatePaginationControls(data.total_count, currentOffset / limit);
        })
        .catch((error) => {
            console.error("Error fetching sessions:", error);
        });
}

// Fetch session details with filters and pagination
function fetchSessionDetails(sessionId, offset = 0, filters = {}) {
    const params = new URLSearchParams({
        session_id: sessionId,
        limit,
        offset,
        ...filters,
    });

    fetch(`/dashboard/api/session-details?${params}`)
        .then((response) => response.json())
        .then((data) => {
            renderSessionDetails(data.details);
            updatePaginationControls(data.total_count, offset / limit);
        })
        .catch((error) => {
            console.error("Error fetching session details:", error);
        });
}

// Initialize session fetching on page load
fetchSessions();