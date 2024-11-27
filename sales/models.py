from django.db import models
from inventory.models import Product  # Direct import of Product model

class Sale(models.Model):
    SalesChoice = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]

    customer_name = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=SalesChoice)

    def __str__(self):
        return f"Sale #{self.id} - {self.customer_name}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items", null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product} x {self.quantity}"
