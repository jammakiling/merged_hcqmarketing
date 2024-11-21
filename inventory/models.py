from django.db import models
from products.models import Product  # Import the Product model from the product app

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    inventory_stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Inventory for {self.product.product_name}"
    

class StockHistory(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name="stock_history")
    purchase = models.ForeignKey('purchases.Purchase', on_delete=models.CASCADE)  # String-based reference
    status = models.CharField(max_length=50)  # "Delivered", "Partially Delivered", etc.
    delivered_quantity = models.PositiveIntegerField()
    remarks = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.inventory.product.product_name} - {self.status} ({self.delivered_quantity})"