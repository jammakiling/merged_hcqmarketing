from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from datetime import datetime
from .models import Purchase, PurchaseItem
from .forms import PurchaseForm, PurchaseItemFormSet
from suppliers.models import Supplier
from inventory.models import Inventory, StockHistory
from .models import Invoice
from .forms import InvoiceForm


def update_inventory_for_item(item, added_quantity, reverse=False):
    """Adjust the inventory stock based on the delivered quantity.
       If reverse=True, we subtract the delivered quantity, otherwise add it."""
    inventory = item.inventory
    if reverse:
        # Subtract the delivered quantity to revert the change
        inventory.inventory_stock -= item.delivered_quantity
    else:
        # Add the newly delivered quantity
        inventory.inventory_stock += added_quantity
    inventory.save()


def log_stock_history(item, status, remarks, quantity):
    """Log stock history for the item."""
    StockHistory.objects.create(
        inventory=item.inventory,
        purchase=item.purchase,
        status=status,
        delivered_quantity=quantity,
        remarks=remarks
    )


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
                    purchase_items = []
                    for form in formset:
                        purchase_item = form.save(commit=False)
                        purchase_item.purchase = purchase
                        if not purchase_item.price:
                            purchase_item.price = purchase_item.inventory.product.purchase_price
                        purchase_item.save()
                        purchase_items.append(purchase_item)
                        total_cost += purchase_item.quantity * purchase_item.price

                    purchase.total_cost = total_cost
                    purchase.save()

                    if purchase.status == 'Delivered':
                        for item in purchase_items:
                            update_inventory_for_item(item, item.quantity)

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


def change_purchase_status(request, id):
    purchase = get_object_or_404(Purchase, id=id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        remarks = request.POST.get('remarks', '')  # Getting remarks from the POST request

        try:
            with transaction.atomic():
                if new_status == 'Pending':
                    for item in purchase.items.all():
                        if item.delivered_quantity > 0:
                            update_inventory_for_item(item, -item.delivered_quantity, reverse=True)
                            item.delivered_quantity = 0
                            item.save()
                    purchase.status = 'Pending'

                elif new_status == 'Partially Delivered':
                    for item in purchase.items.all():
                        delivered_key = f"delivered_quantity_{item.id}"
                        try:
                            newly_delivered_quantity = int(request.POST.get(delivered_key, 0))
                        except ValueError:
                            messages.error(request, f"Invalid input for {item.inventory.product.product_name}.")
                            continue

                        remaining_quantity = item.quantity - item.delivered_quantity

                        if newly_delivered_quantity > remaining_quantity:
                            messages.error(
                                request,
                                f"Cannot deliver more than the remaining quantity for {item.inventory.product.product_name}. "
                                f"Ordered: {item.quantity}, Already Delivered: {item.delivered_quantity}, Remaining: {remaining_quantity}."
                            )
                            continue
                        elif newly_delivered_quantity < 0:
                            messages.error(
                                request,
                                f"Invalid delivery quantity for {item.inventory.product.product_name}. Must be 0 or greater."
                            )
                            continue
                        else:
                            # Update inventory for the newly delivered quantity
                            update_inventory_for_item(item, newly_delivered_quantity)
                            item.delivered_quantity += newly_delivered_quantity
                            item.save()

                            # Log stock history with remarks
                            log_stock_history(item, 'Partially Delivered', remarks, newly_delivered_quantity)

                    purchase.status = 'Partially Delivered'

                elif new_status == 'Delivered':
                    # Ensure all items are fully delivered
                    for item in purchase.items.all():
                        if item.delivered_quantity < item.quantity:
                            remaining_quantity = item.quantity - item.delivered_quantity
                            update_inventory_for_item(item, remaining_quantity)
                            item.delivered_quantity = item.quantity
                            item.save()
                            log_stock_history(item, 'Delivered', remarks, remaining_quantity)

                    purchase.status = 'Delivered'

                    # Inform the user to add invoice details
                    if not hasattr(purchase, 'invoice'):
                        messages.info(request, "Status updated to Delivered. Please add invoice details.")

                purchase.save()
                messages.success(request, f"Purchase {purchase.purchase_code} status updated to {new_status}.")
                return redirect('purchases:purchase_detail', purchase_id=purchase.id)

        except Exception as e:
            messages.error(request, f"Error updating status: {e}")

    return redirect('purchases:purchase_detail', purchase_id=id)

def add_invoice(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)

    if request.method == 'POST':
        # Save the invoice
        invoice_number = request.POST.get('invoice_number')
        invoice_date = request.POST.get('invoice_date')
        shipment_date = request.POST.get('shipment_date')
        remarks = request.POST.get('remarks')

        invoice = Invoice.objects.create(
            purchase=purchase,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            shipment_date=shipment_date,
            remarks=remarks,
        )
        
        # Redirect to purchase detail page after saving the invoice
        return redirect('purchases:purchase_detail', purchase_id=purchase.id)

    return render(request, 'purchases/add_invoice.html', {'purchase': purchase})
def purchase_index(request):
    purchases = Purchase.objects.annotate(product_count=Count('items'))
    for purchase in purchases:
        for item in purchase.items.all():
            item.remaining_quantity = item.quantity - item.delivered_quantity
    return render(request, 'purchases/index.html', {'purchases': purchases})


def purchase_detail(request, purchase_id):
    # Fetch the purchase object using the purchase_id
    purchase = get_object_or_404(Purchase, id=purchase_id)

    # Fetch the associated invoice if the status is "Delivered"
    invoice = None
    if purchase.status == 'Delivered':
        try:
            invoice = Invoice.objects.get(purchase=purchase)
        except Invoice.DoesNotExist:
            invoice = None

    return render(request, 'purchases/purchase_detail.html', {
        'purchase': purchase,
        'invoice': invoice
    })