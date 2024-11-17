from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PurchaseItem

@receiver(post_save, sender=PurchaseItem)
def update_inventory_stock(sender, instance, created, **kwargs):
    if created:
        inventory = instance.inventory
        inventory.inventory_stock += instance.quantity
        inventory.save()
