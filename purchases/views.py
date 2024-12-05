from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import Count
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from datetime import datetime
from .models import Purchase, PurchaseItem
from .forms import PurchaseForm, PurchaseItemFormSet
from suppliers.models import Supplier
from inventory.models import Inventory, StockHistory
from .models import Invoice
from .forms import InvoiceForm
from .forms import PurchaseReturnForm, PurchaseReturnItemForm
# In views.py

from .models import PurchaseReturn, PurchaseReturnItem
from .forms import PurchaseReturnForm, PurchaseReturnItemFormSet



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
                    
                    # **Ensure initial status is 'Pending'**
                    purchase.status = 'Pending'
                    
                    # Generate unique purchase_code
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

                    # **Remove Inventory Update from Initial Save**
                    # if purchase.status == 'Delivered':
                    #     for item in purchase_items:
                    #         update_inventory_for_item(item, item.quantity)

                messages.success(request, f"Purchase {purchase.purchase_code} created successfully with status 'Pending'.")
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



from inventory.models import SerializedInventory

def change_purchase_status(request, id):
    purchase = get_object_or_404(Purchase, id=id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        remarks = request.POST.get('remarks', '')  # Optional remarks field

        try:
            with transaction.atomic():
                all_items_fully_delivered = True  # Flag to check if all items are fully delivered

                if new_status == 'Pending':
                    # Reset delivery for all items and revert inventory
                    for item in purchase.items.all():
                        if item.delivered_quantity > 0:
                            update_inventory_for_item(item, -item.delivered_quantity, reverse=True)
                            item.delivered_quantity = 0
                            item.serial_numbers = ""  # Clear serial numbers
                            item.save()
                    purchase.status = 'Pending'

                elif new_status == 'Partially Delivered':
                    # Update delivery quantities for partial delivery
                    for item in purchase.items.all():
                        delivered_key = f"delivered_quantity_{item.id}"
                        serial_numbers_key = f"serial_numbers_{item.id}"

                        try:
                            newly_delivered_quantity = int(request.POST.get(delivered_key, 0))
                        except ValueError:
                            messages.error(request, f"Invalid input for {item.inventory.product.product_name}.")
                            all_items_fully_delivered = False
                            continue

                        remaining_quantity = item.quantity - item.delivered_quantity

                        if newly_delivered_quantity > remaining_quantity:
                            messages.error(
                                request,
                                f"Cannot deliver more than remaining quantity for {item.inventory.product.product_name}. "
                                f"Ordered: {item.quantity}, Already Delivered: {item.delivered_quantity}, Remaining: {remaining_quantity}."
                            )
                            all_items_fully_delivered = False
                            continue
                        elif newly_delivered_quantity < 0:
                            messages.error(
                                request,
                                f"Invalid delivery quantity for {item.inventory.product.product_name}. Must be 0 or greater."
                            )
                            all_items_fully_delivered = False
                            continue
                        else:
                            # Handle serial numbers only for serialized products
                            if item.inventory.product.is_serialized:  # Assuming `is_serialized` is a boolean field in the product model
                                serial_numbers = request.POST.get(serial_numbers_key, '').split(',')
                                serial_numbers = [s.strip() for s in serial_numbers if s.strip()]
                                if len(serial_numbers) != newly_delivered_quantity:
                                    messages.error(
                                        request,
                                        f"Number of serial numbers provided ({len(serial_numbers)}) does not match "
                                        f"the delivered quantity ({newly_delivered_quantity}) for {item.inventory.product.product_name}."
                                    )
                                    all_items_fully_delivered = False
                                    continue

                                # Create SerializedInventory records for each serial number
                                for serial_number in serial_numbers:
                                    # Save the serial number into the SerializedInventory model
                                    SerializedInventory.objects.create(
                                        inventory=item.inventory,
                                        serial_number=serial_number,
                                        status="Available"  # Or adjust status if needed
                                    )

                                # Add serial numbers to the item for record keeping (if needed)
                                if item.serial_numbers:
                                    item.serial_numbers += "," + ",".join(serial_numbers)
                                else:
                                    item.serial_numbers = ",".join(serial_numbers)

                            # Update inventory and save changes
                            update_inventory_for_item(item, newly_delivered_quantity)
                            item.delivered_quantity += newly_delivered_quantity
                            item.save()

                            # Log stock history
                            log_stock_history(item, 'Partially Delivered', remarks, newly_delivered_quantity)

                        # Check if the current item is fully delivered
                        if item.delivered_quantity < item.quantity:
                            all_items_fully_delivered = False

                    purchase.status = 'Delivered' if all_items_fully_delivered else 'Partially Delivered'

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

                    # Inform user to add invoice details
                    if not hasattr(purchase, 'invoice'):
                        messages.info(request, "Status updated to Delivered. Please add invoice details.")

                purchase.save()
                messages.success(request, f"Purchase {purchase.purchase_code} status updated to {purchase.status}.")
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

def purchase_return_list(request):
    returns = PurchaseReturn.objects.all().order_by('-return_date')
    return render(request, 'purchases/purchase_return.html', {'returns': returns})


from .models import Purchase, PurchaseItem, PurchaseReturn, PurchaseReturnItem
from .forms import PurchaseReturnForm, PurchaseReturnItemFormSet
from django.template.loader import get_template, TemplateDoesNotExist
from django.forms import modelformset_factory

def update_inventory_for_returned_item(item, returned_quantity):
    """Adjust the inventory stock based on the returned quantity."""
    inventory = item.item.inventory
    inventory.inventory_stock -= returned_quantity  # Reduce stock for returned items
    inventory.save()


def log_return_stock_history(item, returned_quantity):
    """Log stock history for the returned items."""
    StockHistory.objects.create(
        inventory=item.item.inventory,
        purchase=item.item.purchase,
        status='Returned',
        delivered_quantity=-returned_quantity,  # Negative for returns
        remarks=f"Returned {returned_quantity} units."
    )


def create_purchase_return(request):
    if request.method == 'POST':
        purchase_return_form = PurchaseReturnForm(request.POST)
        purchase = None

        # Validate the form first
        if purchase_return_form.is_valid():
            # Access cleaned_data only after validation
            purchase = purchase_return_form.cleaned_data.get('purchase')

        # Initialize the formset with the purchase if available
        formset = PurchaseReturnItemFormSet(request.POST, form_kwargs={'purchase': purchase})

        if purchase_return_form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Create the PurchaseReturn object
                    purchase_return = purchase_return_form.save(commit=False)
                    today = datetime.now().strftime("%Y%m%d")
                    latest_return = PurchaseReturn.objects.filter(return_code__startswith=f"PR-{today}").order_by("id").last()
                    next_number = 1 if not latest_return else int(latest_return.return_code.split('-')[-1]) + 1
                    purchase_return.return_code = f"PR-{today}-{next_number:03d}"
                    purchase_return.save()

                    # Process each returned item
                    total_returned_items = 0
                    for form in formset:
                        if form.cleaned_data.get('item') and form.cleaned_data.get('returned_quantity'):
                            purchase_return_item = form.save(commit=False)

                            # Debugging: Print delivered quantity and returned quantity
                            item = purchase_return_item.item
                            delivered_quantity = item.delivered_quantity
                            returned_quantity = purchase_return_item.returned_quantity

                            print(f"Item: {item.inventory.product.product_name}, Delivered Quantity: {delivered_quantity}, Returned Quantity: {returned_quantity}")

                            # Ensure returned quantity does not exceed delivered quantity
                            if returned_quantity > delivered_quantity:
                                messages.error(request, f"Returned quantity for item {item.inventory.product.product_name} exceeds delivered quantity.")
                                return redirect('purchases:create_purchase_return')

                            # Check if delivered_quantity would go negative
                            new_delivered_quantity = delivered_quantity - returned_quantity
                            if new_delivered_quantity < 0:
                                messages.error(request, f"Cannot return more than the delivered quantity for item {item.inventory.product.product_name}.")
                                return redirect('purchases:create_purchase_return')

                            # Update the delivered_quantity field in PurchaseItem
                            item.delivered_quantity = new_delivered_quantity
                            item.save()  # Save the updated item

                            # Link the return item to the return object
                            purchase_return_item.purchase_return = purchase_return
                            purchase_return_item.save()

                            # Update inventory and log stock history
                            update_inventory_for_returned_item(purchase_return_item, returned_quantity)
                            log_return_stock_history(purchase_return_item, returned_quantity)

                            total_returned_items += returned_quantity

                    # Add success message and redirect
                    messages.success(request, f"Purchase return created successfully with {total_returned_items} items returned.")
                    return redirect('purchases:purchase_return_list')

            except Exception as e:
                # Handle transaction failure
                messages.error(request, f"Error saving purchase return: {e}")

        else:
            # Handle form validation errors
            messages.error(request, "There was an error with the submitted forms.")

    else:
        purchase_return_form = PurchaseReturnForm()
        formset = PurchaseReturnItemFormSet(queryset=PurchaseReturnItem.objects.none())

    purchases = Purchase.objects.all()

    return render(request, 'purchases/create_purchase_return.html', {
        'purchase_return_form': purchase_return_form,
        'formset': formset,
        'purchases': purchases,
    })

def get_items_for_purchase(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    items = purchase.items.filter(delivered_quantity__gt=0)  # Ensure items have this field.

    data = {
        "items": [
            {
                "id": item.id,
                "name": item.inventory.product.product_name,
                "delivered_quantity": item.delivered_quantity,  # Confirm correct field name.
            }
            for item in items
        ]
    }

    # Debug output to validate correctness
    print(f"Purchase ID: {purchase_id}, Items: {data['items']}")

    return JsonResponse(data)