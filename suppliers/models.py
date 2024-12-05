from django.db import models
from django.utils import timezone
# Create your models here.


class Supplier(models.Model):

    Supplier_Status = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        
    ]

   # id = models.AutoField(primary_key=True)
    # supplier_number = models.CharField(max_length=50, unique=True)   
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    supplier_hardware = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    address = models.CharField(max_length=100)
    contact_num = models.CharField(max_length=15)
    dateStart = models.DateField("Date Started")
    dateEdit = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=Supplier_Status, default='Active')

    def __str__(self):
        return f"'Supplier: {self.supplier_hardware}"


