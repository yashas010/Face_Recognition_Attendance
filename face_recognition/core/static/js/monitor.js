navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        let videoElement = document.getElementById("cameraFeed");
        videoElement.srcObject = stream;
        
        let lastEmployeeName = "";  // ✅ Stores last employee's name
        let lastStatus = "";  // ✅ Stores last marked status

        setInterval(() => {
            let canvas = document.createElement("canvas");
            canvas.width = videoElement.videoWidth;
            canvas.height = videoElement.videoHeight;
            let ctx = canvas.getContext("2d");
            ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

            // Convert canvas to Blob
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
                    console.log("API Response:", data);
                    
                    let messageElement = document.getElementById("attendanceMessage");

                    if (data.success) {
                        lastEmployeeName = data.data.employee_name;
                        lastStatus = data.data.status;
                        
                        messageElement.innerHTML = `
                            <strong>Employee:</strong> ${lastEmployeeName} (ID: ${data.data.employee_id})<br>
                            <strong>Status:</strong> ${lastStatus}<br>
                            <strong>Time:</strong> ${new Date(data.data.timestamp).toLocaleString()}
                        `;
                    } else {
                        if (data.message) {
                            lastEmployeeName = data.data.employee_name || lastEmployeeName;  // Preserve last name
                            lastStatus = data.data.last_status || lastStatus;  // Preserve last status
                            
                            messageElement.innerHTML = `
                                <strong>Employee:</strong> ${lastEmployeeName} (ID: ${data.data.employee_id})<br>
                                <strong>Message:</strong> ${data.message}<br>
                                <strong>Last Status:</strong> ${lastStatus}
                            `;
                        } else {
                            messageElement.innerText = `Error: ${data.error || "Undefined error"}`;
                        }
                    }
                })
                .catch(error => console.error("Error:", error));

            }, "image/jpeg");
        }, 5000);
    })
    .catch(error => console.error("Camera access denied:", error));

// ✅ Function to Get CSRF Token
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
