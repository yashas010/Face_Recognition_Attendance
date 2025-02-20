from rest_framework import serializers
from .views import *
from django.utils import timezone

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.name", read_only=True)
    employee_id = serializers.IntegerField(source="employee.id", read_only=True)
    formatted_timestamp = serializers.SerializerMethodField()  # Custom formatted timestamp
    class Meta:
        model = AttendanceLog
        fields = ["id", "employee","employee_id", "employee_name", "formatted_timestamp", "status", "face_recognized"]
        
    def get_formatted_timestamp(self, obj):
        """Convert timestamp to local time (IST) and format it."""
        local_time = timezone.localtime(obj.timestamp)  # Converts to Django's default timezone
        return local_time.strftime("%d-%m-%Y %H:%M")  # Format: DD-MM-YYYY HH:MM (24-hour)