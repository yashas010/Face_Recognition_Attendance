from django.db import models

# Create your models here.

# Employee Model
class Employee(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incremented Employee ID
    name = models.CharField(max_length=100)  # Employee Name
    email = models.EmailField(unique=True)  # Unique Email
    photo = models.ImageField(upload_to="employee_photos/")  # Store Employee Face Photo
    created_at = models.DateTimeField(auto_now_add=True)  # When Employee Added

    def __str__(self):
        return self.name  # Display name in admin panel

# Attendance Log Model
class AttendanceLog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Link to Employee
    timestamp = models.DateTimeField(auto_now_add=True)  # Entry Time
    status = models.CharField(max_length=10, choices=[("IN", "Check-In"), ("OUT", "Check-Out")])  # Entry Type
    face_recognized = models.BooleanField(default=False)  # Was Face Matched?

    def __str__(self):
        return f"{self.employee.name} - {self.status} at {self.timestamp}"
