navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        let videoElement = document.getElementById("cameraFeed");
        videoElement.srcObject = stream;

        let lastDetectedEmployees = new Map(); // Store employees with timestamps
        let messageElement = document.getElementById("attendanceMessage");

        function resetMessage() {
            messageElement.innerHTML = `<p>Waiting for scan...</p>`;
        }

        resetMessage(); // Initial message

        setInterval(() => {
            let canvas = document.createElement("canvas");
            canvas.width = videoElement.videoWidth;
            canvas.height = videoElement.videoHeight;
            let ctx = canvas.getContext("2d");
            ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

            canvas.toBlob(blob => {
                let formData = new FormData();
                formData.append("photo", blob, "frame.jpg");

                fetch("http://127.0.0.1:8000/api/attendance/", {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-CSRFToken": getCSRFToken(),
                    },
                    credentials: "include"
                })
                .then(response => response.json())
                .then(data => {
                    console.log("✅ Raw API Response:", data);

                    if (!Array.isArray(data) || data.length === 0) {
                        console.warn("⚠️ No face detected.");
                        resetMessage(); // Reset to "Waiting for scan..."
                        return;
                    }

                    // ✅ Overwrite the message element completely (no duplication)
                    let newMessage = "";

                    let currentTimestamp = Date.now(); // Get current timestamp

                    data.forEach(entry => {
                        if (!entry.data) {
                            console.warn("⚠️ Warning: Missing 'data' field in entry", entry);
                            return;
                        }

                        let employeeName = entry.data.employee_name || "Unknown";
                        let employeeId = entry.data.employee_id || "N/A";
                        let status = entry.data.status !== undefined ? entry.data.status : entry.data.last_status || "N/A";
                        let timestamp = entry.data.timestamp || entry.data.last_entry_time || new Date().toISOString();
                        let message = entry.message || "No message";

                        console.log(`👤 Employee: ${employeeName}, ID: ${employeeId}, Status: ${status}, Time: ${timestamp}`);
                        console.log(`📌 Message: ${message}`);

                        // ✅ Store the employee ID with the current timestamp
                        lastDetectedEmployees.set(employeeId, currentTimestamp);

                        newMessage += `<div class="attendance-entry">`;
                        newMessage += `<p><strong>Employee:</strong> ${employeeName} (ID: ${employeeId})</p>`;
                        if (message.includes("already marked")) {
                            newMessage += `<p><strong>Message:</strong> ${message}</p>`;
                            newMessage += `<p><strong>Last Status:</strong> ${status}</p>`;
                        } else {
                            newMessage += `<p><strong>Status:</strong> ${status}</p>`;
                            newMessage += `<p><strong>Time:</strong> ${new Date(timestamp).toLocaleString()}</p>`;
                        }
                        newMessage += `</div>`;
                    });

                    messageElement.innerHTML = newMessage; // ✅ Replace content, avoid duplication

                })
                .catch(error => {
                    console.error("❌ Fetch error:", error);
                    resetMessage(); // Reset to "Waiting for scan..." on error
                });

            }, "image/jpeg");
        }, 5000);
    })
    .catch(error => console.error("❌ Camera access denied:", error));

function getCSRFToken() {
    let cookieValue = null;
    let cookies = document.cookie.split(";");

    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        if (cookie.startsWith("csrftoken=")) {
            cookieValue = cookie.substring("csrftoken=".length, cookie.length);
            break;
        }
    }
    return cookieValue;
}
