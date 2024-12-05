from datetime import timedelta, timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.forms import modelformset_factory
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from .forms import SalesReturnForm, SalesForm, SalesItemForm, SalesItemFormSet, WalkInCustomerForm
from inventory.models import Inventory
from django.utils import timezone
import logging
from .models import Sales, SalesItem, Customer, Product, Invoice, SalesReturn

# Create Sale
def create_sale(request):
    SaleItemFormSet = modelformset_factory(SalesItem, form=SalesItemForm, extra=1, can_delete=True)
    sale_form = SalesForm(request.POST or None)
    formset = SaleItemFormSet(request.POST or None, queryset=SalesItem.objects.none())

    if request.method == 'POST':
        if sale_form.is_valid() and formset.is_valid():
            sale = sale_form.save(commit=False)
            sale.payment_stat = 'Pending'  # Default payment status
            sale.save()  # Save the sale first to get a primary key for the sale instance

            total_amount = 0
            for item in sale.items.all():
                if item.price_per_item is not None and item.quantity is not None:
                    total_amount += item.price_per_item * item.quantity

            sale.total_amount = total_amount
            sale.save()

            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    sale_item = form.save(commit=False)
                    sale_item.sale = sale
                    if sale_item.price_per_item is not None and sale_item.quantity is not None:
                        sale_item.save()

            for item in sale.items.all():
                product = item.product
                quantity_sold = item.quantity
                inventory_item = Inventory.objects.get(product=product)
                inventory_item.inventory_stock -= quantity_sold
                inventory_item.save()

            messages.success(request, 'Sale has been processed and inventory updated.')
            return redirect('sales:sales_list')
        else:
            messages.error(request, 'There was an error creating the sale. Please check the details.')

    return render(request, 'sales/add.html', {
        'sale_form': sale_form,
        'formset': formset,
        'customers': Customer.objects.all(),
        'products': Product.objects.all(),
        'inventories': Inventory.objects.all(),
    })

def walk_in_sale(request):
    # Get all products
    products = Product.objects.all()

    if request.method == 'POST':
        sale_form = SalesForm(request.POST)
        walk_in_form = WalkInCustomerForm(request.POST)

        if sale_form.is_valid() and walk_in_form.is_valid():
            # Save walk-in customer
            customer_name = walk_in_form.cleaned_data['customer_name']
            walk_in_customer, created = Customer.objects.get_or_create(
                customer_hardware="Walk-In", first_name=customer_name, last_name=''
            )

            # Now, set the walk-in customer explicitly in the SalesForm
            sale = sale_form.save(commit=False)  # Do not save yet
            sale.customer = walk_in_customer  # Set the customer for this sale
            sale.save()  # Save the sale with the customer

            # Optionally save purchased products
            return redirect('sales:sales_list')  # Redirect to the sales list or another page

    else:
        sale_form = SalesForm()  # Default form without a customer
        walk_in_form = WalkInCustomerForm()

    context = {
        'sale_form': sale_form,
        'walk_in_form': walk_in_form,
        'products': products,
    }
    return render(request, 'sales/walk_in.html', context)

# Get Products for Sale
def get_products(request):
    products = Product.objects.all()
    product_list = [{'id': product.id, 'name': product.product_name, 'price': product.product_price} for product in products]
    return JsonResponse(product_list, safe=False)

# Add an Invoice to a Sale
def add_invoice(request, sale_id):
    sale = Sales.objects.get(id=sale_id)
    
    invoice = Invoice(
        sale=sale,
        invoice_number="INV-123456",  # Example invoice number
        invoice_date=timezone.now().date(),
        shipment_date=timezone.now().date() + timedelta(days=7),
    )
    invoice.save()

    sale.sales_invoice = invoice
    sale.save()

    return redirect('sales:sales_detail', sale_id=sale.id)

# Update Sale Items
def update_sale_items(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)
    if request.method == 'POST':
        sale_items = request.POST.getlist('sale_items')
        for item_data in sale_items:
            item_id, new_quantity = item_data.split(":")
            sale_item = SalesItem.objects.get(id=item_id)
            sale_item.quantity = int(new_quantity)
            sale_item.save()
        messages.success(request, 'Sale items updated successfully.')
        return redirect('sales:sales_detail', sale_id=sale.id)
    return render(request, 'sales/update_sale_items.html', {'sale': sale})

# Delete Sale Item
def delete_sale_item(request, sale_id, item_id):
    sale = get_object_or_404(Sales, id=sale_id)
    sale_item = get_object_or_404(SalesItem, id=item_id)
    sale_item.delete()
    messages.success(request, 'Sale item deleted successfully.')
    return redirect('sales:sales_detail', sale_id=sale.id)

# Change Sales Status
def change_sale_status(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        sale.status = new_status
        sale.save()
        messages.success(request, f'Sales status changed to {new_status}.')
        return redirect('sales:sales_detail', sale_id=sale.id)
    return redirect('sales:sales_list')

# Delete Sale
def delete_sale(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)
    sale.delete()
    messages.success(request, 'Sale deleted successfully.')
    return redirect('sales:sales_list')

# Sales List
def sales_list(request):
    sales = Sales.objects.all().order_by('-date')
    return render(request, 'sales/index.html', {'sales': sales})

# Sales Detail
def sales_detail(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)
    items = sale.salesitem_set.all()
    return render(request, 'sales/sales_detail.html', {'sale': sale, 'items': items})

# Edit Sale
def edit_sale(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)
    SaleItemFormSet = modelformset_factory(SalesItem, form=SalesItemForm, extra=1, can_delete=True)
    sale_form = SalesForm(request.POST or None, instance=sale)
    formset = SaleItemFormSet(request.POST or None, queryset=sale.salesitem_set.all())

    if request.method == 'POST':
        if sale_form.is_valid() and formset.is_valid():
            sale = sale_form.save(commit=False)
            sale.save()

            total_amount = 0
            for item in formset:
                if item.cleaned_data and not item.cleaned_data.get('DELETE', False):
                    sale_item = item.save(commit=False)
                    sale_item.sale = sale
                    sale_item.save()

            for item in sale.salesitem_set.all():
                product = item.product
                quantity_sold = item.quantity
                inventory_item = Inventory.objects.get(product=product)
                inventory_item.inventory_stock -= quantity_sold
                inventory_item.save()

            messages.success(request, 'Sale has been updated successfully.')
            return redirect('sales:sales_detail', sale_id=sale.id)

    return render(request, 'sales/edit_sale.html', {
        'sale_form': sale_form,
        'formset': formset,
        'sale': sale,
        'customers': Customer.objects.all(),
        'products': Product.objects.all(),
    })

# Create Sales Return
def create_sales_return(request, sale_id):
    sale = get_object_or_404(Sales, pk=sale_id)
    last_return = SalesReturn.objects.filter(sales=sale).order_by('-id').first()
    if last_return:
        last_return_number = int(last_return.return_code[3:])
        new_return_code = f"SAR{last_return_number + 1:05d}"
    else:
        new_return_code = "SAR00001"

    if request.method == "POST":
        quantity = request.POST.get('quantity')
        date = request.POST.get('date')

        sales_return = SalesReturn(
            sales=sale,
            return_code=new_return_code,
            quantity=quantity,
            date=date,
        )
        sales_return.save()

        sale.status = "Returned"
        sale.save()

        return redirect('sales:sales_list')

    return render(request, 'sales/create_sales_return.html', {'sale': sale, 'return_code': new_return_code})

def sales_return_list(request):
    sales_returns = SalesReturn.objects.all().order_by('-date')
    return render(request, 'sales/sales_return_list.html', {'sales_returns': sales_returns})

# Invoice List
def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-invoice_date')
    return render(request, 'sales/invoice_list.html', {'invoices': invoices})