from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from .models import Product
from django.shortcuts import render, get_object_or_404, redirect


from .forms import ProductForm

# Create your views here.
def index(request):
    return render(request, 'products/index.html', {
        'products':Product.objects.all().order_by('id')
    })

def view_product(request, id):
    product = Product.objects.get(pk=id)
    return HttpResponseRedirect(reverse('index'))

def add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'products/add.html', {
                'form': ProductForm(),  # Reset the form after successful submission
                'success': True,  # Indicate success
            })
    else:
        form = ProductForm()
    return render(request, 'products/add.html', {'form': form})
    
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products_index')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_edit.html', {'form': form})
