from django.db import models

class Employees(models.Model):
    # ID, Last Name, First Name, Middle Name, Job Title,
    JOB_TITLE = [
        ('Secretary', 'Secretary'),
        ('Executive Secretary', 'Executive Secretary'),
       
    ]   

    # employee_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=50, choices=JOB_TITLE)  # figure this out 

