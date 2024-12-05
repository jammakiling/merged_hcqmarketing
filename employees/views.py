from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Employees
from .forms import EmployeeForm
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q

def employee_index(request):
    search_query = request.GET.get('search', '')
    if search_query:
        employees = Employees.objects.filter(
            Q(id__icontains=search_query) | Q(full_name__icontains=search_query)
        ).order_by('id')
        results_count = employees.count()
        messages.info(request, f"{results_count} result(s) found for '{search_query}'.")
    else:
        employees = Employees.objects.all().order_by('id')
        results_count = 0 

    return render(request, 'employees/index.html', {
        'employees': employees,
        'results_count': results_count 
    })

def employees_detail(request, pk):
    # Ensure you're correctly fetching the employee
    employee = get_object_or_404(Employees, pk=pk)

    return render(request, 'employees/details.html', {'employee': employee})

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