import cv2
import numpy as np
import faiss
import json
import time
from django.core.files.storage import default_storage
from insightface.app import FaceAnalysis

# Initializing the Model
app = FaceAnalysis(providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))  # Use CPU with 640x640 detection size

# Initializing the FAISS index
embedding_dim = 512  # ArcFace produces 512-dimensional embeddings
faiss_index = faiss.IndexFlatL2(embedding_dim)  # L2 distance-based FAISS index
employee_id_map = []  # Stores Employee IDs mapped to FAISS index positions

def extract_single_face_embedding(image_path):
    """Extract a single face embedding from an image."""
    start_time = time.time() 
    img = cv2.imread(image_path)
    
    if img is None:
        print(f"❌ Error: Unable to read image at {image_path}")
        return None  

    faces = app.get(img)  # Detect faces

    if not faces:
        print("⚠ No face detected in the image.")
        return None  

    print("✅ Face detected, extracting embedding...")

    embedding = faces[0].embedding  
    end_time = time.time()
    print(f"⏱ extract_single_face_embedding took {end_time - start_time:.4f} seconds")  

    return np.array(embedding)  # Convert to NumPy array

def extract_face_embeddings(image_path):
    """Extract embeddings for multiple faces in an image."""
    start_time = time.time() 
    img = cv2.imread(image_path)
    
    if img is None:
        print(f"❌ Error: Unable to read image at {image_path}")
        return None  

    faces = app.get(img)  

    if not faces:
        print("⚠ No face detected in the image.")
        return None  

    print(f"✅ Detected {len(faces)} face(s) in the image")  

    embeddings = [face.embedding for face in faces]  
    end_time = time.time()

    print(f"⏱ extract_face_embeddings took {end_time - start_time:.4f} seconds")  
    return embeddings  

def load_employee_embeddings():
    """Load all employee embeddings into FAISS at startup."""
    from core.models import Employee  # Import inside function to avoid circular imports

    global faiss_index, employee_id_map
    faiss_index.reset()  # Clear FAISS index before reloading
    employee_id_map = []  

    employees = Employee.objects.exclude(face_embedding__isnull=True).exclude(face_embedding="")

    if not employees.exists():
        print("⚠ No employees with stored embeddings in the database.")
        return

    embeddings = []
    for employee in employees:
        embedding = employee.get_embedding()
        if embedding is not None:
            embeddings.append(embedding)
            employee_id_map.append(employee.id)  

    if embeddings:
        embeddings_np = np.array(embeddings, dtype=np.float32)  
        faiss_index.add(embeddings_np)  
        print(f"✅ Loaded {len(embeddings)} employee embeddings into FAISS")

def match_faces(uploaded_photo):
    """Match an uploaded face against stored employee embeddings using FAISS."""
    from core.models import Employee

    total_start_time = time.time()  

    # Save uploaded image temporarily
    start_time = time.time()
    temp_path = default_storage.save('temp_face.jpg', uploaded_photo)
    end_time = time.time()
    print(f"⏱ Image saving took {end_time - start_time:.4f} seconds")

    # Extract face embeddings
    start_time = time.time()
    uploaded_embeddings = extract_face_embeddings(default_storage.path(temp_path))
    end_time = time.time()
    print(f"⏱ Embedding extraction took {end_time - start_time:.4f} seconds")

    if uploaded_embeddings is None:
        default_storage.delete(temp_path)
        return None, "No face detected in uploaded image"

    #  Search FAISS for matches
    start_time = time.time()

    uploaded_embeddings_np = np.array(uploaded_embeddings, dtype=np.float32)  
    D, I = faiss_index.search(uploaded_embeddings_np, k=1)  # Find top-1 closest match

    end_time = time.time()
    print(f"⏱ FAISS search took {end_time - start_time:.4f} seconds")

    matched_employees = []
    for i, index in enumerate(I):  
        if index[0] == -1:  
            continue

        employee_id = employee_id_map[index[0]]  
        employee = Employee.objects.get(id=employee_id)

        # Calculate cosine similarity (optional, if FAISS uses L2 distance)
        similarity = np.dot(uploaded_embeddings_np[i], employee.get_embedding()) / (
            np.linalg.norm(uploaded_embeddings_np[i]) * np.linalg.norm(employee.get_embedding())
        )

        if similarity > 0.55:  # Adjust threshold as needed
            print(f"✅ Match found: {employee.name} (Similarity: {similarity:.4f})")
            matched_employees.append(employee)

    # Cleanup temporary image
    default_storage.delete(temp_path)

    total_end_time = time.time()  
    print(f"⏱ Total match_faces execution time: {total_end_time - total_start_time:.4f} seconds")

    if matched_employees:
        print(f"✅ Total Matched Employees: {len(matched_employees)}")
        return matched_employees, None
    return None, "No matching employee found"
