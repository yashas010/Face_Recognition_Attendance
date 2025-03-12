from django.db import models
import json  # Built-in, no installation needed
import numpy as np  # Requires 'pip install numpy' if not installed


# Create your models here.

# Employee Model
class Employee(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incremented Employee ID
    name = models.CharField(max_length=100)  # Employee Name
    email = models.EmailField(unique=True)  # Unique Email
    photo = models.ImageField(upload_to="employee_photos/")  # Store Employee Face Photo
    created_at = models.DateTimeField(auto_now_add=True)
    face_embedding = models.JSONField(null=True, blank=True)
    def set_embedding(self, embedding):
        """Save embedding as a JSON string."""
        if embedding is None:
            print("❌ Error: Cannot save None embedding!")
            return

        print(f"🔍 Debug: Embedding type before saving: {type(embedding)}")

        if not isinstance(embedding, np.ndarray):
            print("⚠ Warning: Expected NumPy array, got", type(embedding))

        self.face_embedding = json.dumps(embedding.tolist())  # Convert to JSON string
        print("✅ Embedding stored successfully")

    def get_embedding(self):
        """Retrieve embedding as a NumPy array."""
        return np.array(json.loads(self.face_embedding)) if self.face_embedding else None

    def save(self, *args, **kwargs):
        """Override save to generate face embedding when a photo is uploaded."""
        super().save(*args, **kwargs)  # Save instance first

        if self.photo:  # If photo is uploaded
            # Import inside function
            from core.arcface_model import extract_single_face_embedding
            image_path = self.photo.path
            print(f"Extracting embeddings from: {image_path}")  # Get image file path
            embedding = extract_single_face_embedding(image_path)

            if embedding is not None:
                self.set_embedding(embedding)
                super().save(update_fields=['face_embedding'])  # Save embedding

    # Attendance Log Model
class AttendanceLog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Link to Employee
    timestamp = models.DateTimeField(auto_now_add=True)  # Entry Time
    status = models.CharField(max_length=10, choices=[("IN", "Check-In"), ("OUT", "Check-Out")])  # Entry Type
    face_recognized = models.BooleanField(default=False)  # Was Face Matched?
    

    def __str__(self):
        return f"{self.employee.name} - {self.status} at {self.timestamp}"
