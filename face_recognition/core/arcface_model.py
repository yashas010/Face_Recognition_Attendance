import cv2
import numpy as np
import onnxruntime
import insightface
from insightface.app import FaceAnalysis
from django.core.files.storage import default_storage
import inspect
import json  # For handling stored embeddings

# Initialize Face Recognition Model
app = FaceAnalysis(providers=['CPUExecutionProvider'])

# Check the signature of the prepare method to inspect parameters
print(inspect.signature(app.prepare))

# Use the correct way to call prepare, without 'nms' as a direct parameter
app.prepare(ctx_id=0, det_size=(640, 640))  # CPU mode with detection size

def extract_face_embeddings(image_path):
    img = cv2.imread(image_path)
        
        # ✅ Check if image is loaded properly
    if img is None:
        print(f"Error: Unable to read image at {image_path}")  # Debugging output
        return None  # Return None if image loading fails

    faces = app.get(img)

    if not faces:
        print("⚠ No face detected in the image.")
        return None  # No face detected
    print("✅ Face detected, extracting embedding...")
    return faces[0].embedding  # Return first detected face embedding
 # Return first detected face embedding


def match_face(uploaded_photo):
    """
    Compares uploaded face with stored embeddings in the database.
    """
    from core.models import Employee
    # Save temp file
    temp_path = default_storage.save('temp_face.jpg', uploaded_photo)

    # Extract embedding for uploaded photo
    uploaded_embedding = extract_face_embeddings(default_storage.path(temp_path))
    if uploaded_embedding is None:
        default_storage.delete(temp_path)
        return None, "No face detected in uploaded image"

    print("Uploaded face embedding extracted")
    
    # Compare with stored embeddings
    employees = Employee.objects.exclude(face_embedding__isnull=True).exclude(face_embedding="")

    min_distance = float('inf')
    matched_employee = None

    for employee in employees:
        employee_embedding = employee.get_embedding()
        if employee_embedding is None:
            continue

        # Compute cosine similarity
        similarity = np.dot(uploaded_embedding, employee_embedding) / (
            np.linalg.norm(uploaded_embedding) * np.linalg.norm(employee_embedding)
        )

        print(f"Comparing with {employee.name} (ID: {employee.id}) - Similarity: {similarity}")

        if similarity > 0.55:  # Adjust threshold as needed
            matched_employee = employee
            print(f"Match found with {employee.name} (ID: {employee.id})")  
            break  

    # Cleanup temp file
    default_storage.delete(temp_path)

    if matched_employee:
        return matched_employee, None
    return None, "No matching employee found"
