from django.db import models
from suppliers.models import Supplier
from inventory.models import Inventory
import uuid
from django.core.exceptions import ValidationError

class Purchase(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Partially Delivered', 'Partially Delivered'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchases')
    date = models.DateTimeField(auto_now_add=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    purchase_code = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Purchase {self.purchase_code} from {self.supplier.supplier_hardware} on {self.date}"

    def save(self, *args, **kwargs):
        if not self.purchase_code:  # Generate code only if it doesn't exist
            self.purchase_code = f"PUR-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='purchase_items')
    quantity = models.PositiveIntegerField(default=0)
    delivered_quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    serial_numbers = models.TextField(blank=True, null=True)  # New field to store serial numbers

    def __str__(self):
        return f"{self.inventory.product.product_name} ({self.quantity})"

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.inventory.product.purchase_price
        super().save(*args, **kwargs)


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    ]

    TERM_CHOICES = [
        ('30 Days', '30 Days'),
        ('60 Days', '60 Days'),
        ('90 Days', '90 Days'),
    ]

    purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField()
    cargo_name = models.CharField(max_length=100)
    cargo_number = models.CharField(max_length=50)
    shipment_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unpaid')
    term = models.CharField(max_length=10, choices=TERM_CHOICES, default='30 Days')
    checked_by = models.CharField(max_length=100)
    received_by = models.CharField(max_length=100)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.purchase.purchase_code}"
    
    # In models.py

class PurchaseReturn(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    return_date = models.DateField(auto_now_add=True)

class PurchaseReturnItem(models.Model):
    purchase_return = models.ForeignKey(PurchaseReturn, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(PurchaseItem, on_delete=models.CASCADE, null=True, blank=False)
    returned_quantity = models.PositiveIntegerField()

    def clean(self):
        if self.returned_quantity > self.item.quantity_delivered:
            raise ValidationError("Return quantity cannot exceed the delivered quantity.")
