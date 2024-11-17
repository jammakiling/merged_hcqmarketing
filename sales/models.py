from django.db import models

class Sales(models.Model):
    product_name = models.CharField(max_length=100)
   

    def __str__(self):
        return f"{self.product_name} from {self.supplier_name}"