from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name','last_name','customer_hardware','email','address','contact_num','dateStart','startBy','status']

        
        
        labels = {
            # 'customer_number': 'Customer Number',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'customer_hardware': 'Customer Hardware',
            'email': 'Email',
            'address': 'Address',
            'contact_num': 'Contact Number',
            'dateStart': 'Date Started',
            'startBy': 'Started By',
            'status': 'Status',
        }   
        widgets = {
          #  'customer_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_hardware': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control','rows': 3}),
            'contact_num': forms.TextInput(attrs={'class': 'form-control'}),
            'dateStart': forms.DateInput(attrs={'class': 'form-control','type': 'date'}),
            'startBy': forms.Select(attrs={'class': 'form-control'}),
             'status': forms.Select(attrs={'class': 'form-control'}),
        }   

    