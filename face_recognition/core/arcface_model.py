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

def extract_single_face_embedding(image_path):
    img = cv2.imread(image_path)
    
    # ✅ Check if image is loaded properly
    if img is None:
        print(f"Error: Unable to read image at {image_path}")  # Debugging output
        return None  # Return None if image loading fails

    faces = app.get(img)  # Detect faces

    if not faces:
        print("⚠ No face detected in the image.")
        return None  # No face detected

    print("✅ Face detected, extracting embedding for registration...")

    embedding = faces[0].embedding  # Directly extract

    print(f"🔍 Debug: Extracted embedding type: {type(embedding)}")

    return np.array(embedding)  # Explicitly convert to NumPy array


def extract_face_embeddings(image_path):
    img = cv2.imread(image_path)
    
    # ✅ Check if image is loaded properly
    if img is None:
        print(f"Error: Unable to read image at {image_path}")  # Debugging output
        return None  # Return None if image loading fails

    faces = app.get(img)  # Detect faces

    if not faces:
        print("⚠ No face detected in the image.")
        return None  # No face detected

    print(f"✅ Detected {len(faces)} face(s) in the image")  # Debugging output

    embeddings = [face.embedding for face in faces]  # Extract embeddings for all faces
    
    return embeddings  # Return a list of embeddings



def match_faces(uploaded_photo):
    from core.models import Employee

    temp_path = default_storage.save('temp_face.jpg', uploaded_photo)
    uploaded_embeddings = extract_face_embeddings(default_storage.path(temp_path))

    if uploaded_embeddings is None:
        default_storage.delete(temp_path)
        return None, "No face detected in uploaded image"

    employees = Employee.objects.exclude(face_embedding__isnull=True).exclude(face_embedding="")
    matched_employees = []

    for embedding in uploaded_embeddings:  # Loop over all detected embeddings
        for employee in employees:
            employee_embedding = employee.get_embedding()
            if employee_embedding is None:
                continue

            similarity = np.dot(embedding, employee_embedding) / (
                np.linalg.norm(embedding) * np.linalg.norm(employee_embedding)
            )

            if similarity > 0.55:  # Adjust threshold as needed
                print(f"✅ Match found: {employee.name} (Similarity: {similarity:.4f})")
                matched_employees.append(employee)

    default_storage.delete(temp_path)

    if matched_employees:
        print(f"✅ Total Matched Employees: {len(matched_employees)}")
        return matched_employees, None
    return None, "No matching employee found"

