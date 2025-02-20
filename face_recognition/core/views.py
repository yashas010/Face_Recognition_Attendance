from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.models import *
from core.serializers import EmployeeSerializer, AttendanceSerializer
from core.arcface_model import match_face, extract_face_embeddings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from datetime import timedelta
# Create your views here.

def index(request):
    return render(request, 'index.html')
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

def monitor_panel(request):
    return render(request, 'monitor_panel.html')





@api_view(['GET'])
def health_check(request):
    return Response({'status': 'API is running!'}, status=200)
    
#to register new employee 
@csrf_exempt  
@api_view(['POST'])
def register_employee(request):
    name = request.data.get('name')
    email = request.data.get('email')
    photo = request.FILES.get('photo')

    if not name or not email or not photo:
        return Response({"error": "Name, email, and photo are required!"}, status=400)

    # Check if email already exists
    if Employee.objects.filter(email=email).exists():
        return Response({"error": "Email already registered!"}, status=400)

    # Check if the same photo already exists
    if Employee.objects.filter(photo=f"employee_photos/{photo.name}").exists():
        return Response({"error": "This photo is already associated with another employee!"}, status=400)

    # Create new employee
    employee = Employee.objects.create(name=name, email=email, photo=photo)
    embedding = extract_face_embeddings(employee.photo.path)
    if embedding is not None:
        employee.set_embedding(embedding)
        employee.save()


    return Response({
        "success": True,
        "message": "Employee registered successfully!",
        "data": {
            "id": employee.id,
            "name": employee.name,
            "email": employee.email,
            "photo_url": employee.photo.url
        }
    }, status=201)



#to get all employees
@api_view(['GET'])
def get_allemployees(request):
    employees = Employee.objects.all()
    serializer = EmployeeSerializer(employees, many=True)
    
    return Response({
        "success": True,
        "message": "All employees fetched successfully",
        "data": serializer.data
    }, status=200)


#get employee by id
@api_view(['GET'])
def get_employee(request, id):
    try:
        employee = Employee.objects.get(id=id)
        serializer = EmployeeSerializer(employee)
        return Response({
            "success": True,
            "message": "Employee fetched successfully",
            "data": serializer.data
        }, status=200)

    except Employee.DoesNotExist:
        return Response({
            "success": False,
            "message": "Employee not found"
        }, status=404)


# update api for employee   
@api_view(['PATCH'])  # Changed to PATCH for partial updates 
def update_employee(request, id):
    employee = get_object_or_404(Employee, id=id)
    
    serializer = EmployeeSerializer(employee, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({
            "success": True,
            "message": "Employee updated successfully",
            "data": serializer.data
        }, status=200)
    
    return Response({
        "success": False,
        "message": "Invalid data",
        "errors": serializer.errors
    }, status=400)


@api_view(['DELETE'])
def delete_employee(request, id):
    employee = get_object_or_404(Employee, id=id)
    employee.delete()

    return Response({
        "success": True,
        "message": "Employee deleted successfully!"
    }, status=200)

    
#to get all attendance records
@api_view(['GET'])
def get_attendance_records(request):
    try:
        logs = AttendanceLog.objects.all().order_by('-timestamp')  # Fetch all logs, latest first
        serializer = AttendanceSerializer(logs, many=True)
        
        return Response({
            "success": True,
            "message": "Attendance records fetched successfully.",
            "data": serializer.data
        }, status=200)
    
    except Exception as e:
        return Response({
            "success": False,
            "message": "Failed to fetch attendance records.",
            "error": str(e)
        }, status=500)





'''handling the attendance of employees(the monitor panel)
  '''
@csrf_exempt
@api_view(['POST'])
def mark_attendance(request):
    """
    Marks attendance based on face recognition.
    """
    uploaded_photo = request.FILES.get('photo')

    if not uploaded_photo:
        return Response({"success": False, "error": "Photo is required"}, status=400)

    matched_employee, error_message = match_face(uploaded_photo)

    if not matched_employee:
        return Response({"success": False, "error": error_message}, status=404)

    # ✅ Check last attendance entry for the employee
    last_entry = AttendanceLog.objects.filter(employee=matched_employee).order_by('-timestamp').first()

    # ✅ Time threshold (1 minute)
    time_threshold = timedelta(minutes=1)

    if last_entry and (now() - last_entry.timestamp) < time_threshold:
        return Response({
            "success": False,
            "message": f"Attendance already marked recently ({last_entry.status})",
            "data": {
                "employee_id": matched_employee.id,
                "employee_name": matched_employee.name,
                "last_entry_time": str(last_entry.timestamp),
                "last_status": last_entry.status
            }
        }, status=200)

    # ✅ Toggle IN/OUT status
    new_status = "OUT" if last_entry and last_entry.status == "IN" else "IN"

    # ✅ Save new attendance entry
    attendance_entry = AttendanceLog.objects.create(
        employee=matched_employee,
        status=new_status,
        face_recognized=True
    )

    return_data = {
        "success": True,
        "message": f"Attendance marked successfully: {new_status}",
        "data": {
            "id": attendance_entry.id,
            "timestamp": str(attendance_entry.timestamp),
            "status": new_status,
            "employee_id": matched_employee.id,
            "employee_name": matched_employee.name
        }
    }

    print("Returning API Response:", json.dumps(return_data, indent=4))  # ✅ Debug log
    return Response(return_data, status=201)


            
           


