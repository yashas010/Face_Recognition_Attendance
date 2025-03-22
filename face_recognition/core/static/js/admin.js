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

async function loadEmployees() {
    const table = document.getElementById("employeeTable");
    const tbody = table.querySelector("tbody");
    tbody.innerHTML = "";

    try {
        const response = await fetch("/api/employees/");
        const data = await response.json();

        data.data.forEach(employee => {
            let row = `<tr>
                <td>${employee.id}</td>
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

        document.getElementById("employeeTable").style.display = "table";
        document.getElementById("attendanceTable").style.display = "none";
    } catch (error) {
        console.error("Error loading employees:", error);
    }
}

async function loadAttendanceLogs() {
    const logTable = document.getElementById("attendanceTable");
    const tbody = logTable.querySelector("tbody");
    tbody.innerHTML = "";

    try {
        const response = await fetch("/api/attendance-records/");
        const data = await response.json();

        data.data.forEach(log => {
            let row = `<tr>
                <td>${log.employee_id}</td>
                <td>${log.employee_name}</td>
                <td>${log.formatted_timestamp}</td>
                <td>${log.status}</td>
            </tr>`;
            tbody.innerHTML += row;
        });

        document.getElementById("attendanceTable").style.display = "table";
        document.getElementById("employeeTable").style.display = "none";
    } catch (error) {
        console.error("Error loading attendance logs:", error);
    }
}

document.getElementById("viewEmployeesBtn").addEventListener("click", loadEmployees);
document.getElementById("viewAttendanceLogsBtn").addEventListener("click", loadAttendanceLogs);

// Edit Employee
// async function editEmployee(id, currentName, currentEmail) {
//     let newName = prompt("Enter new name:", currentName);
//     let newEmail = prompt("Enter new email:", currentEmail);

//     if (!newName || !newEmail) return;

//     const csrftoken = getCookie('csrftoken');

//     try {
//         const response = await fetch(`/api/employee/${id}/update/`, {
//             method: "PATCH",
//             headers: {
//                 "Content-Type": "application/json",
//                 "X-CSRFToken": csrftoken
//             },
//             body: JSON.stringify({ name: newName, email: newEmail })
//         });

//         const data = await response.json();

//         if (data.success) {
//             alert("Employee updated successfully!");
//             loadEmployees(); // Refresh only the employee table
//         } else {
//             alert("Error: " + (data.message || "Failed to update employee."));
//         }
//     } catch (error) {
//         console.error("Error:", error);
//     }
// }


// Edit Employee
async function editEmployee(id, currentName, currentEmail) {
    let newName = prompt("Enter new name:", currentName);
    let newEmail = prompt("Enter new email:", currentEmail);

    if (!newName || !newEmail) return;

    const csrftoken = getCookie('csrftoken');

    try {
        const response = await fetch(`/api/employee/${id}/update/`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({ name: newName, email: newEmail })
        });

        const data = await response.json();

        if (data.success) {
            alert("Employee updated successfully!");
            await loadEmployees(); // Refresh only the employee table
        } else {
            alert("Error: " + (data.message || "Failed to update employee."));
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

// 


// Delete Employee
async function deleteEmployee(id) {
    const csrftoken = getCookie('csrftoken');

    if (!confirm("Are you sure you want to delete this employee?")) return;

    try {
        const response = await fetch(`/api/employee/${id}/delete/`, {
            method: "DELETE",
            headers: { "X-CSRFToken": csrftoken }
        });

        const data = await response.json();

        if (data.success) {
            alert("Employee deleted successfully!");
            await loadEmployees(); // Refresh only the employee table
        } else {
            alert("Error: " + (data.message || "Failed to delete employee."));
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

// Add Employee
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
            loadEmployees(); // Refresh employee table after adding
        } else {
            alert("Error: " + (data.error || "Failed to register employee."));
        }
    } catch (error) {
        console.error("Error:", error);
    }
});
