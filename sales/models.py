from django.db import models
from django.utils import timezone
from inventory.models import Product
from customers.models import Customer

class Sales(models.Model):
    SALES_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('Online', 'Online'),
        ('Terms', 'Terms'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='sales')
    date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sales_code = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, choices=SALES_STATUS_CHOICES, default='Pending')
    payment_stat = models.CharField(max_length=50, choices=PAYMENT_CHOICES, default='Cash')
    sales_invoice = models.OneToOneField('Invoice', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'sales_sales'  # This explicitly sets the table name

    def generate_sales_code(self):
        """Generate a unique sales code in the format SAL-YYYYMMDD-XXXX."""
        today = timezone.now().date()
        date_str = today.strftime("%Y%m%d")

        last_sale = Sales.objects.filter(date__date=today).order_by('-id').first()

        if last_sale and last_sale.sales_code:
            last_code_number = int(last_sale.sales_code.split('-')[-1])
            new_code_number = last_code_number + 1
        else:
            new_code_number = 1

        return f"SAL-{date_str}-{new_code_number:04d}"

    def calculate_total_amount(self):
        """Calculate the total sale amount from its items."""
        total = sum(item.total_price for item in self.items.all())
        return total

    def update_stock(self):
        """Update product stock when sale is completed."""
        if self.status == 'Completed':
            for item in self.items.all():
                if item.product.stock >= item.quantity:
                    item.product.stock -= item.quantity
                    item.product.save()
                else:
                    raise ValueError(f"Insufficient stock for {item.product.product_name}")

    def save(self, *args, **kwargs):
        """Override save to ensure sales_code generation and total_amount calculation."""
        if not self.sales_code:
            self.sales_code = self.generate_sales_code()
        super().save(*args, **kwargs)
        self.total_amount = self.calculate_total_amount()
        super().save(update_fields=['total_amount'])

    def __str__(self):
        return f"Sale {self.sales_code} - {self.customer.customer_name}"


class SalesItem(models.Model):
    sale = models.ForeignKey(Sales, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def total_price(self):
        """Calculate the total price for this sale item."""
        return self.quantity * self.price_per_item

    def save(self, *args, **kwargs):
        """Override save to automatically update related sales."""
        if not self.price_per_item:
            self.price_per_item = self.product.product_price
        super().save(*args, **kwargs)
        self.sale.total_amount = self.sale.calculate_total_amount()
        self.sale.save(update_fields=['total_amount'])

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity} @ {self.price_per_item}"


class Invoice(models.Model):
    sale = models.OneToOneField(Sales, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField()
    shipment_date = models.DateField()
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} for Sale {self.sale.sales_code}"


class SalesReturn(models.Model):
    return_code = models.CharField(max_length=100, unique=True)
    sales = models.ForeignKey(Sales, related_name="sales_returns", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    date = models.DateField()

    class Meta:
        db_table = 'sales_salesreturn'  # This explicitly sets the table name

    def save(self, *args, **kwargs):
        """Override save to handle inventory adjustments."""
        super().save(*args, **kwargs)
        for item in self.sales.items.all():
            product = item.product
            inventory_stock = product.stock
            product.stock += self.quantity
            product.save()

    def __str__(self):
        return f"Return {self.return_code} for Sale {self.sales.sales_code}"
