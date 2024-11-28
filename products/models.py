from django.db import models

# Create your models here.
class Product(models.Model):
    product_code = models.CharField(max_length=100, default='DEFAULT_CODE')
    product_name = models.CharField(max_length=100)
    product_descript = models.TextField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_unit = models.CharField(max_length=50)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Price from supplier (optional)
    is_serialized = models.BooleanField(default=False)  # New field

    def __str__(self):
        return f"Product: {self.product_name}"
