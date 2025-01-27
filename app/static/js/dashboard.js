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

// Close modal
document.getElementById('close-modal').addEventListener('click', () => {
    document.getElementById('session-modal').style.display = "none";
});