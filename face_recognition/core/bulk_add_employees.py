import os
import django
import json
import numpy as np
from django.core.files import File
from core.models import Employee
from core.arcface_model import extract_single_face_embedding

# Django setup (if running as standalone script)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "face_recognition.settings")  
django.setup()

# 🔹 Folder where images are stored  
IMAGE_FOLDER = "core\photos"

# Get all image files
image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.endswith(('.jpg', '.png', '.jpeg'))]

print(f"🖼 Found {len(image_files)} images. Registering employees...")

bulk_employees = []
for idx, image_name in enumerate(image_files, start=1):
    image_path = os.path.join(IMAGE_FOLDER, image_name)
    
    # 🔍 Extract face embedding
    embedding = extract_single_face_embedding(image_path)
    if embedding is None:
        print(f"⚠ Skipping {image_name}: No face detected.")
        continue  # Skip images with no face
    
    # 🏷 Generate a name (based on filename)
    name = os.path.splitext(image_name)[0].replace("_", " ").title()
    email = f"{name.lower().replace(' ', '_')}@example.com"  # Fake email
    
    # 📝 Create Employee instance (without saving yet)
    employee = Employee(
        name=name,
        email=email,
        face_embedding=json.dumps(embedding.tolist())  # Store embedding
    )
    
    bulk_employees.append(employee)

# 🚀 Bulk insert into the database
if bulk_employees:
    Employee.objects.bulk_create(bulk_employees)
    print(f"✅ Successfully added {len(bulk_employees)} employees!")
else:
    print("❌ No employees were added.")

