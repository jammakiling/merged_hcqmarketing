from django import forms
from .models import Purchase, PurchaseItem, PurchaseReturn, PurchaseReturnItem
from django.forms import ValidationError, modelformset_factory
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
            'status': forms.HiddenInput(),
        }

    def save(self, commit=True):
        purchase = super().save(commit=False)
        purchase.status = 'Pending'  # Ensure status is always 'Pending' on creation
        if commit:
            purchase.save()
        return purchase

class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ['inventory', 'quantity', 'price', 'serial_numbers']  # Added serial_numbers field
        widgets = {
            'inventory': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'serial_numbers': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter serial numbers, separated by commas',
            }),  # Widget for serial numbers
        }

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        serial_numbers = cleaned_data.get('serial_numbers')

        if serial_numbers:
            serial_list = [s.strip() for s in serial_numbers.split(',') if s.strip()]
            if len(serial_list) != quantity:
                raise forms.ValidationError(
                    f"The number of serial numbers ({len(serial_list)}) must match the quantity ({quantity})."
                )
        return cleaned_data

PurchaseItemFormSet = modelformset_factory(PurchaseItem, form=PurchaseItemForm, extra=1)

class PurchaseReturnForm(forms.ModelForm):
    class Meta:
        model = PurchaseReturn
        fields = ['purchase']

    def clean_purchase(self):
        purchase = self.cleaned_data.get('purchase')
        if not purchase:
            raise ValidationError("A valid purchase must be selected.")
        return purchase

class PurchaseReturnItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseReturnItem
        fields = ['item', 'returned_quantity']

    def __init__(self, *args, **kwargs):
        purchase = kwargs.pop('purchase', None)
        super().__init__(*args, **kwargs)
        if purchase:
            self.fields['item'].queryset = PurchaseItem.objects.filter(purchase=purchase)
        else:
            self.fields['item'].queryset = PurchaseItem.objects.none()


    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        returned_quantity = cleaned_data.get('returned_quantity')

        if not item:
            raise ValidationError("An item must be selected.")

        if item.delivered_quantity is None:
            raise ValidationError("The selected item does not have a valid delivered quantity.")

        if returned_quantity is not None and item.delivered_quantity is not None:
            if returned_quantity > item.delivered_quantity:
                raise ValidationError(f"Returned quantity ({returned_quantity}) cannot exceed delivered quantity ({item.delivered_quantity}).")

        return cleaned_data

PurchaseReturnItemFormSet = modelformset_factory(
    PurchaseReturnItem,
    form=PurchaseReturnItemForm,
    extra=1,  # Allows one extra blank form for input
    can_delete=True  # Enables the ability to delete rows in the formset
)
