from django.db import models
from products.models import Product  # Import the Product model from the product app

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    inventory_stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Inventory for {self.product.product_name}"