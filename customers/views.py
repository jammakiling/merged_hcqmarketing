
from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.urls import reverse
from .models import Customer
from .forms import CustomerForm
from django.contrib import messages
from django.db.models import Q

def index(request):
    search_query = request.GET.get('search', '')
    if search_query:
        customers = Customer.objects.filter(
            Q(id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(customer_hardware__icontains=search_query)
        ).order_by('id')
        results_count = customers.count()
        messages.info(request, f"{results_count} result(s) found for '{search_query}'.")
    else:
        customers = Customer.objects.all().order_by('id')
        results_count = 0

    return render(request, 'customers/index.html', {
        'customers': customers,
        'results_count': results_count 
    })

def view_customer(request, id):
    customer = Customer.objects.get(pk=id)
    return HttpResponseRedirect(reverse('index'))

def add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            # Create a new customer from the form data
            new_customer = form.save()
            return render(request, 'customers/add.html', {
                'form': CustomerForm(),  # Reset the form after successful submission
                'success': True  # Indicate success
            })
        else:
            # If the form is not valid, return it with errors
            return render(request, 'customers/add.html', {
                'form': form  # Pass the form with errors back to the template
            }) 
    else:
        # For GET requests, display a blank form
        form = CustomerForm()
        return render(request, 'customers/add.html', {
            'form': form
        })
    
def delete(request, id):

    customer = get_object_or_404(Customer, id=id)
    
    if request.method == 'POST':
        customer = Customer.objects.get(pk=id)
        messages.success(request, 'Customer deleted successfully.')
        customer.delete()
    return HttpResponseRedirect(reverse('customers_index'))

def edit(request, id):
    customer = get_object_or_404(Customer, id=id)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customers_index')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customers/edit.html', {'form': form, 'customer': customer})