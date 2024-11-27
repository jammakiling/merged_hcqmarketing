from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction  # To ensure atomic transactions
from .forms import SalesForm, SaleItemFormSet
from .models import Sale, SaleItem
from inventory.models import Product  # Assuming the Product model is in the inventory app

def index(request):
    """
    View to display a list of all sales.
    """
    sales = Sale.objects.all()
    return render(request, 'sales/index.html', {'sales': sales})

def add(request):
    """
    View to create a new sales order.
    """
    if request.method == 'POST':
        sale_form = SalesForm(request.POST)
        formset = SaleItemFormSet(request.POST)

        if sale_form.is_valid() and formset.is_valid():
            try:
                # Ensure all operations are atomic
                with transaction.atomic():
                    # Save the sale
                    sale = sale_form.save()

                    # Save the sale items and update inventory
                    items = formset.save(commit=False)
                    for item in items:
                        item.sale = sale

                        # Check inventory stock before saving
                        product = item.product
                        if product.stock < item.quantity:
                            raise ValueError(f'Not enough stock for {product.product_name}.')

                        # Deduct the stock
                        product.stock -= item.quantity
                        product.save()

                        # Save the sale item
                        item.save()

                    # Commit the formset deletions (if any)
                    formset.save_m2m()

                    messages.success(request, 'Sale created successfully!')
                    return redirect('sales_index')  # Redirect to the sales list

            except ValueError as e:
                # Rollback transaction and show error message
                messages.error(request, str(e))
            except Exception as e:
                # Handle unexpected errors
                messages.error(request, 'An error occurred while processing the sale. Please try again.')
        else:
            messages.error(request, 'There were errors in your form submission.')

    else:
        sale_form = SalesForm()
        formset = SaleItemFormSet()

    return render(request, 'sales/add.html', {
        'sale_form': sale_form,
        'formset': formset,
    })
