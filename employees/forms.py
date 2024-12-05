from django import forms
from .models import Employees

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employees
        fields = ['full_name', 'address', 'phone', 'email', 'job_title', 'dateStart', 'status', 'emergency_name', 'emergency_contact']
        labels = {
            'full_name': 'Full Name',
            'address': 'Address',  
            'phone': 'Phone',
            'email': 'Email',
            'job_title': 'Job Title',
            'dateStart': 'Date Started',
            'status': 'Status',
            'emergency_name': 'Emergency Contact Name',  
            'emergency_contact': 'Emergency Contact Number',
        }

        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Leave blank if none', 'class': 'form-control'}),
            'job_title': forms.Select(attrs={'class': 'form-control'}),
            'dateStart': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'emergency_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
        }