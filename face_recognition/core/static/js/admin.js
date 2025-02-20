function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.getElementById("addEmployeeForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    let formData = new FormData();
    let csrftoken = getCookie('csrftoken');
    formData.append("name", document.getElementById("name").value);
    formData.append("email", document.getElementById("email").value);
    formData.append("photo", document.getElementById("photo").files[0]);

    try {
        let response = await fetch("/api/register/", {
            method: "POST",
            headers: { "X-CSRFToken": csrftoken },
            body: formData
        });

        let data = await response.json();
        
        if (data.success) {
            alert(data.message);
            document.getElementById("addEmployeeForm").reset();
        } else {
            alert("Error: " + (data.error || "Failed to register employee."));
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred while adding employee.");
    }
});

// Fetch and display employees
document.getElementById("viewEmployeesBtn").addEventListener("click", function () {
    fetch("/api/employees/")
        .then(response => response.json())
        .then(data => {
            let table = document.getElementById("employeeTable");
            table.style.display = "block";
            let tbody = table.querySelector("tbody");
            tbody.innerHTML = "";

            data.data.forEach(employee => {
                let row = `<tr>
                    <td>${employee.name}</td>
                    <td>${employee.email}</td>
                    <td><img src="${employee.photo_url}" width="50"></td>
                    <td>
                        <button onclick="editEmployee(${employee.id}, '${employee.name}', '${employee.email}')">Edit</button>
                        <button onclick="deleteEmployee(${employee.id})">Delete</button>
                    </td>
                </tr>`;
                tbody.innerHTML += row;
            });
        });
});

// Edit employee
// Update employee
function editEmployee(id, currentName, currentEmail) {
    let newName = prompt("Enter new name:", currentName);
    let newEmail = prompt("Enter new email:", currentEmail);
    
    if (!newName || !newEmail) return;

    let csrftoken = getCookie('csrftoken');

    fetch(`/api/employee/${id}/update/`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify({ name: newName, email: newEmail })  // Send JSON data
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Employee updated successfully!");
            location.reload();
        } else {
            alert("Error: " + (data.message || "Failed to update employee."));
        }
    })
    .catch(error => console.error("Error:", error));
}

// Delete employee
function deleteEmployee(id) {
    let csrftoken = getCookie('csrftoken');

    fetch(`/api/employee/${id}/delete/`, {
        method: "DELETE",
        headers: { "X-CSRFToken": csrftoken } // CSRF token added
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Employee deleted successfully!");
            location.reload();
        } else {
            alert("Error: " + (data.message || "Failed to delete employee."));
        }
    })
    .catch(error => console.error("Error:", error));
}


// Fetch attendance logs
document.getElementById("viewAttendanceLogsBtn").addEventListener("click", function () {
    fetch("/api/attendance-records/")
        .then(response => response.json())
        .then(data => {
            let logTable = document.getElementById("attendanceTable");
            logTable.style.display = "block";
            let tbody = logTable.querySelector("tbody");
            tbody.innerHTML = "";

            data.data.forEach(log => {
                let row = `<tr>
                    <td>${log.employee_name}</td>
                    <td>${log.timestamp}</td>
                    <td>${log.status}</td>
                </tr>`;
                tbody.innerHTML += row;
            });
        })
        .catch(error => console.error("Error:", error));
});
