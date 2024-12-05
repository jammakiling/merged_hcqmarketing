from datetime import datetime
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
    return_code = models.CharField(max_length=20)  # Add return_code field to ensure uniqueness

    def save(self, *args, **kwargs):
        if not self.return_code:  # Only generate return_code if it's not already set
            today = datetime.now().strftime("%Y%m%d")
            latest_return = PurchaseReturn.objects.filter(return_code__startswith=f"PR-{today}").order_by("id").last()
            next_number = 1 if not latest_return else int(latest_return.return_code.split('-')[-1]) + 1
            self.return_code = f"PR-{today}-{next_number:03d}"
        super().save(*args, **kwargs)  # Save the model after generating the return_code

    def __str__(self):
        return f"Return {self.return_code} for Purchase {self.purchase.id}"

from django.core.exceptions import ValidationError
class PurchaseReturnItem(models.Model):
    purchase_return = models.ForeignKey(PurchaseReturn, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(PurchaseItem, on_delete=models.CASCADE, null=True, blank=False)
    returned_quantity = models.PositiveIntegerField()

    def clean(self):
        # Ensure the item is selected
        if not self.item:
            raise ValidationError("An item must be selected for the purchase return.")

        # Handle NoneType for delivered_quantity by defaulting to 0
        delivered_quantity = self.item.delivered_quantity or 0

        # Ensure returned_quantity does not exceed delivered_quantity
        if self.returned_quantity > delivered_quantity:
            raise ValidationError(
                f"Returned quantity ({self.returned_quantity}) cannot exceed delivered quantity ({delivered_quantity})."
            )

    def save(self, *args, **kwargs):
        # Run the clean method before saving
        self.full_clean()
        super().save(*args, **kwargs)