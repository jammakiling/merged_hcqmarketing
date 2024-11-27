from django.urls import path
from . import views


urlpatterns = [
    path('employees/', views.employee_index, name='employees_index'),
    path('employees/add/', views.add, name='add_employee'), 
    path('delete/<int:id>/', views.delete, name='delete_employee'),
]
