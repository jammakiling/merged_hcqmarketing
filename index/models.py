from django.db import models

# Create your models here.


class Index(models.Model):
    # Define your fields here
    name = models.CharField(max_length=100)