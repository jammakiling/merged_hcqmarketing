from django.shortcuts import render
from .models import Inventory  # Import Inventory model
from django.shortcuts import get_object_or_404
from inventory.models import StockHistory

def inventory_index(request):
    inventories = Inventory.objects.all().order_by('id')  # Fetch all Inventory records
    return render(request, 'inventory/index.html', {
        'inventories': inventories  # Pass Inventory objects to the template
    })


def product_detail(request, product_id):
    inventory = get_object_or_404(Inventory, product__id=product_id)
    stock_history = StockHistory.objects.filter(inventory=inventory).order_by('-timestamp')
    return render(request, 'inventory/product_detail.html', {
        'inventory': inventory,
        'stock_history': stock_history,
    })