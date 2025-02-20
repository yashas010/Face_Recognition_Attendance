
from django.urls import path
from .views import index, admin_dashboard, monitor_panel

urlpatterns = [
    path('', index, name='index'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('monitor-panel/', monitor_panel, name='monitor_panel'),
]
