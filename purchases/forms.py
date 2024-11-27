from django import forms
from .models import Purchase, PurchaseItem, PurchaseReturn, PurchaseReturnItem
from django.forms import modelformset_factory
from .models import Invoice
from django.forms import modelformset_factory

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


class PurchaseReturnForm(forms.ModelForm):
    class Meta:
        model = PurchaseReturn
        fields = ['purchase']

class PurchaseReturnItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseReturnItem
        fields = ['item', 'returned_quantity']

    def __init__(self, *args, **kwargs):
        purchase=None
        if "purchase" in kwargs:
            purchase=kwargs.pop("purchase")
        super().__init__(*args, **kwargs)
        # Dynamically filter items based on purchase
        if purchase:
            self.fields['item'].queryset = PurchaseItem.objects.filter(purchase=purchase)

PurchaseReturnItemFormSet = modelformset_factory(
    PurchaseReturnItem,
    form=PurchaseReturnItemForm,
    extra=1,  # Allows one extra blank form for input
    can_delete=True  # Enables the ability to delete rows in the formset
)