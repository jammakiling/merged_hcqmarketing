from django import forms
from django.forms import inlineformset_factory
from .models import Sale, SaleItem
class SalesForm(forms.ModelForm):
   
    class Meta:
        model = Sale
        fields = ['customer_name', 'total_cost','status', ] 
        labels = {
      
            'customer_name': 'Customer Name',
            'total_cost': 'Total',
            'status': 'Status',
            
        }   
        widgets = {
            'customer_name': forms.Select(attrs={'class': 'form-control'}),
            'total_cost': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),

        }

# Define the inline formset for SaleItem
SaleItemFormSet = inlineformset_factory(
    Sale,
    SaleItem,
    fields=['product', 'quantity', 'price_per_unit'],
    extra=1,  # Allows for an additional empty form in the set
    can_delete=True,  # Allows items to be removed
    widgets={
        'product': forms.Select(attrs={'class': 'form-control'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        'price_per_unit': forms.TextInput(attrs={'class': 'form-control'}),
    }
)