from django import forms
from .models import Purchase, PurchaseItem
from django.forms import modelformset_factory
from .models import Invoice

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'invoice_number', 'invoice_date', 'cargo_name', 'cargo_number',
            'shipment_date', 'status', 'term', 'checked_by', 'received_by', 'remarks'
        ]
        widgets = {
            'invoice_date': forms.DateInput(attrs={'type': 'date'}),
            'shipment_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['supplier', 'status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ['inventory', 'quantity', 'price']
        widgets = {
            'inventory': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

PurchaseItemFormSet = modelformset_factory(PurchaseItem, form=PurchaseItemForm, extra=1)
