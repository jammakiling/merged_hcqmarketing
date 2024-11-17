from django.shortcuts import render, redirect
from .models import Sales


def sales_index(request):
    sales = Sales.objects.all()
    return render(request, 'sales/index.html', {'sales': sales})



