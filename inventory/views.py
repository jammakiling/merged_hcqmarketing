from django.shortcuts import render
from .models import Inventory  # Import Inventory model
from django.shortcuts import get_object_or_404
from inventory.models import StockHistory
from django.shortcuts import render, get_object_or_404
from .models import Inventory, StockHistory, SerializedInventory

def inventory_index(request):
    inventories = Inventory.objects.all().order_by('id')
    return render(request, 'inventory/index.html', {
        'inventories': inventories,
    })




def product_detail(request, product_id):
    inventory = get_object_or_404(Inventory, product__id=product_id)
    stock_history = StockHistory.objects.filter(inventory=inventory).order_by('-timestamp')
    
    # Include serialized items if the product has serialized stock
    serialized_items = None
    if hasattr(inventory.product, 'is_serialized') and inventory.product.is_serialized:
        serialized_items = SerializedInventory.objects.filter(inventory=inventory)
        print(f"Serialized items found: {serialized_items}")  # Debugging line

    return render(request, 'inventory/product_detail.html', {
        'inventory': inventory,
        'stock_history': stock_history,
        'serialized_items': serialized_items,
    })