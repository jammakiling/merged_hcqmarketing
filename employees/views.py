from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Employees
from .forms import EmployeeForm
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

def employee_index(request):
    return render(request, 'employees/index.html', {
        'employees': Employees.objects.all().order_by('id')
    })

# View for adding a new employee
def add(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()  # This saves the employee to the database
            messages.success(request, "Employee Added Successfully")
            return redirect('employees_index')  # Redirect to the employee list page
        else:
            messages.error(request, "Failed to add employee. Please check the form.")
    else:
        form = EmployeeForm()

    return render(request, 'employees/add.html', {'form': form})

def delete(request, id):
    employees = get_object_or_404(Employees, id=id)

    if request.method == 'POST':
        employees = Employees.objects.get(pk=id)
        messages.success(request, 'Employee deleted successfully.')
        employees.delete()
        return HttpResponseRedirect(reverse('employees_index'))

    return redirect('employees_index') 
