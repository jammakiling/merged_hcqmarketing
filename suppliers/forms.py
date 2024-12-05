from django import forms
from .models import Supplier

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['first_name','last_name','supplier_hardware','email','address','contact_num','dateStart','dateEdit','status']
        labels = {
           # 'supplier_number': 'Supplier Number',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'supplier_hardware': 'Supplier Hardware Name',
            'email': 'Email',
            'address': 'Address',
            'contact_num': 'Contact Number',
            'dateStart': 'Date Started',
            'dateEdit': 'Date Edited',
            'status': 'Status',
        }   
        widgets = {
            # 'supplier_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier_hardware': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control','rows': 3}),
            'contact_num': forms.TextInput(attrs={'class': 'form-control'}),
            'dateStart': forms.DateInput(attrs={'class': 'form-control','type': 'date'}),
            'dateEdit': forms.DateInput(attrs={'class': 'form-control','type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }