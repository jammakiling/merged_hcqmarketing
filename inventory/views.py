from django.shortcuts import render
from .models import Inventory  # Import Inventory model

def inventory_index(request):
    inventories = Inventory.objects.all().order_by('id')  # Fetch all Inventory records
    return render(request, 'inventory/index.html', {
        'inventories': inventories  # Pass Inventory objects to the template
    })