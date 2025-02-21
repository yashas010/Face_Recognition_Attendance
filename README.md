
# Face Recognition Attendance System (Django + ArcFace)

## Introduction

This is a **Face Recognition Attendance System** built using the **ArcFace model** and **Django** as the backend. The system allows an **Admin Panel** for managing employees and viewing attendance logs, while the **Monitor Panel** runs live face recognition to mark attendance.

## Features

- **Admin Panel:** Manage employees (CRUD operations) and view attendance logs.
- **Monitor Panel:** Live face recognition for automatic attendance marking.
- **Database:** Uses PostgreSQL as the database backend.
- **Face Recognition:** Utilizes the ArcFace model for accurate identification.

## Open Source Libraries Used

- **Django** - Web framework for backend development.
- **InsightFace** - Face recognition model.
- **ONNX & ONNXRuntime** - Optimized deep learning model execution.
- **OpenCV** - Image processing and real-time computer vision.
- **NumPy** - Numerical computations.

## About ArcFace

ArcFace is a highly efficient deep learning-based face recognition model that enhances the discriminative power by using an additive angular margin loss. It provides robust and accurate face verification and identification, making it suitable for real-world attendance systems.

## Prerequisites

Ensure you have the following installed:

- **Python 3.9+**
- **PostgreSQL 13+**
- **pip**
- **Visual Studio C++ Build Tools (for insightface installation)**

## Installation Guide

### Step 1: Clone the Repository

```sh
 git clone <repo_link>
 cd Face_Recognition_Attendance/face_recognition
```

### Step 2: Install Dependencies

Ensure you have **virtual environment** installed. If not, install it first:

```sh
pip install virtualenv
```

Then, create and activate a virtual environment:

```sh
python -m venv venv  # Create virtual environment
source venv/bin/activate  # Activate on macOS/Linux
venv\Scripts\activate  # Activate on Windows
```

Now, install the required dependencies:

```sh
pip install -r requirements.txt
```

### Step 3: Setup PostgreSQL Database

1. Install PostgreSQL from [official site](https://www.postgresql.org/download/).
2. Open **pgAdmin** or connect using the terminal.
3. Create a new database named `Face Attendance`.
4. Modify **database settings** in `face_recognition/settings.py`:

```python
DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "Face Attendance",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

### Step 4: Apply Migrations

```sh
python manage.py migrate
```

### Step 5: Create a Superuser

To access the **Admin Panel**, create a superuser:

```sh
python manage.py createsuperuser
```

Follow the prompts to set up the admin credentials.

### Step 6: Install InsightFace and Dependencies

InsightFace requires **Visual Studio C++ Build Tools** on Windows. Install it from [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/). Once installed, run:

```sh
pip install insightface onnxruntime onnx numpy opencv-python
```

### Step 7: Start the Server

```sh
python manage.py runserver
```

Access the application at:

- **Landing Page:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Admin Panel:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## Application Flow

- **Landing Page:** Provides two options:
  - **Admin Panel**: For CRUD operations (register, update, delete employees) and viewing attendance logs.
  - **Monitor Panel**: Activates the live camera and displays attendance responses.

## Folder Structure

```
Face_Recognition_Attendance/
│   manage.py
│   requirements.txt
│   db.sqlite3
│
├── core/
│   ├── admin.py
│   ├── api_urls.py
│   ├── arcface_model.py
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── migrations/
│   ├── static/
│   │   ├── css/
│   │   │   ├── style.css
│   │   ├── js/
│   │   │   ├── admin.js
│   │   │   ├── monitor.js
│   ├── templates/
│   │   ├── index.html
│   │   ├── admin_dashboard.html
│   │   ├── monitor_panel.html
│
├── face_recognition/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│
├── media/
│   ├── employee_photos/
```

## Contributing

For contributions, create a feature branch and submit a pull request.

## License

This project is licensed under [MIT License](LICENSE).


