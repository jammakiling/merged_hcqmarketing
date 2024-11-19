from django.contrib import messages
from datetime import datetime
from .models import Purchase, PurchaseItem
from .forms import PurchaseForm, PurchaseItemFormSet
from suppliers.models import Supplier
from inventory.models import Inventory
from django.db.models import Count
from django.shortcuts import render, redirect
from django.db import transaction
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from .models import Purchase
def add_purchase(request):
    if request.method == "POST":
        purchase_form = PurchaseForm(request.POST)
        formset = PurchaseItemFormSet(request.POST, queryset=PurchaseItem.objects.none())

        if purchase_form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    purchase = purchase_form.save(commit=False)
                    today = datetime.now().strftime("%Y%m%d")
                    latest_purchase = Purchase.objects.filter(purchase_code__startswith=f"PUR-{today}").order_by("id").last()
                    next_number = 1 if not latest_purchase else int(latest_purchase.purchase_code.split('-')[-1]) + 1
                    purchase.purchase_code = f"PUR-{today}-{next_number:03d}"
                    purchase.save()

                    total_cost = 0
                    purchase_items = []  # Store items to update inventory later if needed
                    for form in formset:
                        purchase_item = form.save(commit=False)
                        purchase_item.purchase = purchase
                        if not purchase_item.price:
                            purchase_item.price = purchase_item.inventory.product.purchase_price
                        purchase_item.save()
                        purchase_items.append(purchase_item)  # Save for later use
                        total_cost += purchase_item.quantity * purchase_item.price

                    purchase.total_cost = total_cost
                    purchase.save()

                    # Update inventory if status is 'Delivered'
                    if purchase.status == 'Delivered':
                        for item in purchase_items:  # Iterate through the saved purchase items
                            update_inventory(item)

                return redirect('purchases:purchase_index')

            except IntegrityError as e:
                messages.error(request, f"Error saving purchase: {e}")
        else:
            messages.error(request, "There was an error with the form submission.")

    else:
        purchase_form = PurchaseForm()
        formset = PurchaseItemFormSet(queryset=PurchaseItem.objects.none())

    suppliers = Supplier.objects.all()
    inventories = Inventory.objects.all()

    return render(request, 'purchases/add_purchase.html', {
        'purchase_form': purchase_form,
        'formset': formset,
        'suppliers': suppliers,
        'inventories': inventories,
    })


def update_inventory(purchase_item):
    # Access the related inventory through the purchase_item's inventory
    inventory = purchase_item.inventory  # Get the inventory linked to the purchase item
    inventory.inventory_stock += purchase_item.quantity  # Increase inventory stock based on the quantity received
    inventory.save()  # Save the updated inventory


def change_purchase_status(request, id):
    if request.method == 'POST':
        purchase = get_object_or_404(Purchase, id=id)
        new_status = request.POST.get('status')

        # Change status
        purchase.status = new_status
        purchase.save()

        # Update inventory if necessary (if status is 'Delivered')
        if new_status == 'Delivered':
            # Iterating over all purchase items related to this purchase
            for purchase_item in purchase.items.all():  # 'items' is the related_name from PurchaseItem
                inventory = purchase_item.inventory  # Access the inventory linked to the purchase item
                print(f"Product: {inventory.product.product_name}, Quantity: {purchase_item.quantity}")
                update_inventory(purchase_item)  # Pass the purchase_item to update inventory

        return redirect('purchases:purchase_index')  # Redirect back to the index page

    return redirect('purchases:purchase_index')


def purchase_detail(request, id):
    # Fetch the purchase object by its ID
    purchase = get_object_or_404(Purchase, id=id)

    # Pass the purchase object to the template
    return render(request, 'purchases/purchase_detail.html', {'purchase': purchase})




def purchase_index(request):
    purchases = Purchase.objects.annotate(product_count=Count('items'))
    return render(request, 'purchases/index.html', {'purchases': purchases})