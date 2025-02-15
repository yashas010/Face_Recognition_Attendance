from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.models import *
from core.serializers import EmployeeSerializer, AttendanceSerializer
# Create your views here.
@api_view(['GET'])
def health_check(request):
    return Response({'status': 'API is running!'}, status=200)
    
#to register new employee   
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
@api_view(['PUT', 'PATCH'])
def update_employee(request, id):
    try:
        employee = Employee.objects.get(id=id)
    except Employee.DoesNotExist:
        return Response({
            "success": False,
            "message": "Employee not found"
        }, status=404)

    serializer = EmployeeSerializer(employee, data=request.data, partial=(request.method == 'PATCH'))

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
    try:
        employee = Employee.objects.get(id=id)
        employee.delete()

        return Response({
            "success": True,
            "message": "Employee deleted successfully!"
        }, status=200)

    except Employee.DoesNotExist:
        return Response({
            "success": False,
            "message": "Employee not found!"
        }, status=404)

    except Exception as e:
        return Response({
            "success": False,
            "message": "Failed to delete employee.",
            "error": str(e)
        }, status=500)

    
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
   for the testing purpose, as a dummy part, sending id through post
   in real time we will be using camera to capture the image and send it to the server'''

@api_view(['POST'])
def mark_attendance(request):
    """
    Marks attendance for an employee based on face recognition.
    """
    employee_id = request.data.get('employee_id')

    if not employee_id:
        return Response({"success": False, "error": "Employee ID is required"}, status=400)

    try:
        employee = Employee.objects.get(id=employee_id)

        # Determine IN or OUT based on last entry
        last_entry = AttendanceLog.objects.filter(employee=employee).order_by('-timestamp').first()
        new_status = "OUT" if last_entry and last_entry.status == "IN" else "IN"

        # Create and save attendance entry
        attendance_entry = AttendanceLog.objects.create(
            employee=employee,
            status=new_status,
            face_recognized=True  # Will be updated dynamically with ArcFace
        )

        return Response({
            "success": True,
            "message": f"Attendance marked successfully: {new_status}",
            "data": AttendanceSerializer(attendance_entry).data
        }, status=201)

    except Employee.DoesNotExist:
        return Response({"success": False, "error": "Employee not found"}, status=404)

    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=500)



            
           
    

