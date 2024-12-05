from django import forms
from .models import Sales, SalesItem, SalesReturn
from inventory.models import Product
from django.forms import modelformset_factory
from customers.models import Customer

# Sales Form for main sale details
class SalesForm(forms.ModelForm):
    class Meta:
        model = Sales
        fields = ['customer', 'status', 'payment_stat']

        labels = {
            'customer': 'Customer Name',
            'status': 'Sale Status',
            'payment_stat': 'Payment Status',
        }

        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'payment_stat': forms.Select(attrs={'class': 'form-control'}),
        }

class SalesItemForm(forms.ModelForm):
    class Meta:
        model = SalesItem
        fields = ['product', 'quantity', 'price_per_item']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'price_per_item': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super(SalesItemForm, self).__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.all()
        self.fields['price_per_item'].required = False

    def clean_price_per_item(self):
        price = self.cleaned_data.get('price_per_item')
        product = self.cleaned_data.get('product')

        if price and product and price != product.product_price:
            raise forms.ValidationError(f"Price must be {product.product_price} for this product.")
        
        return price

class SalesReturnForm(forms.ModelForm):
    class Meta:
        model = SalesReturn
        fields = ['return_code', 'quantity', 'date']

# Formset for managing multiple SalesItems dynamically
SalesItemFormSet = modelformset_factory(
    SalesItem,
    form=SalesItemForm,
    extra=1,
    can_delete=True
)

class WalkInCustomerForm(forms.Form):
    customer_name = forms.CharField(max_length=100, required=True, label="Customer Name")