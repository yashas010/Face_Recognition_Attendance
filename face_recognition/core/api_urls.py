from django.urls import path,include
from .views import register_employee, get_allemployees,get_employee,update_employee,delete_employee,mark_attendance,get_attendance_records,health_check,index

urlpatterns = [
    

    path('check/', health_check, name='check'),  # Define an API route
    path('register/', register_employee, name='register-employee'),  
    path('employees/', get_allemployees, name='get_employees'),
    path('employee/<int:id>/', get_employee, name='get_employee'),
    path('employee/<int:id>/update/', update_employee, name='update_employee'),
    path('employee/<int:id>/delete/', delete_employee, name='delete_employee'),
    path('attendance-records/', get_attendance_records, name='get_attendance_records'),


    #monitor panel paths
    path('attendance/', mark_attendance, name='mark_attendance'),


    
]
