from django.db import models
from phonenumber_field.modelfields import PhoneNumberField  

class Employees(models.Model):
    # ID, Last Name, First Name, Middle Name, Job Title,
    JOB_TITLE = [
        ('Accounting', 'Accounting'),
        ('Checker', 'Checker'),
        ('Driver', 'Driver'),
        ('Guard', 'Guard'),
        ('Sales Agent', 'Sales Agent'),
        ('Secretary', 'Secretary'),
        ('Warehouse Helper', 'Warehouse Helper'),
    ]   

    Employee_Status = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Suspended', 'Suspended'),
        ('Terminated', 'Terminated'),
    ]

    # employee_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=200)
    address = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True)
    email = models.EmailField(blank=True, null=True)
    job_title = models.CharField(max_length=50, choices=JOB_TITLE)
    dateStart = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Employee_Status, default='Active')
    emergency_name = models.CharField(max_length=200, null=True, blank=True)
    emergency_contact = models.CharField(max_length=15, null=True, blank=True)

    # Add other fields if necessary
    
