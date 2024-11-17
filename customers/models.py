from django.db import models
from django.utils import timezone
# Create your models here.
class Customer(models.Model):

    CUSTOMER_START_BY = [
        ('Office', 'Office'),
        ('Agent', 'Agent'),
       
    ]   

    # customer_number = models.PositiveIntegerField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    customer_hardware = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    address = models.CharField(max_length=100)
    contact_num = models.CharField(max_length=15)
    dateStart = models.DateField("Date Started") 
    startBy = models.CharField(max_length=10, choices=CUSTOMER_START_BY)  # figure this out 
    dateEdit = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"'Customer: {self.customer_hardware}"