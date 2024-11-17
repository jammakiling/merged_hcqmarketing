from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'product_descript', 'product_price', 'purchase_price', 'product_unit']  # Added purchase_price to fields
        labels = {
            'product_name': 'Product Name',
            'product_descript': 'Description',
            'product_price': 'Price',
            'purchase_price': 'Purchase Price',  # Added label for purchase_price
            'product_unit': 'Unit',
        }   
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'product_descript': forms.TextInput(attrs={'class': 'form-control'}),
            'product_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control'}),  # Added widget for purchase_price
            'product_unit': forms.TextInput(attrs={'class': 'form-control'}),
        }

