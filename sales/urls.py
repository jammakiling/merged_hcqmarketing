from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # Sales List and Detail Views
    path('sales/', views.sales_list, name='sales_list'),  # Access sales at root of the sales section
    path('<int:sale_id>/details/', views.sales_detail, name='sales_detail'),  # Detailed info about a specific sale

    # Sales Creation and Editing
    path('create/', views.create_sale, name='create_sale'),  # Create a new sale
    path('sale/edit/<int:sale_id>/', views.edit_sale, name='edit_sale'),  # Edit a sale
    path('<int:sale_id>/delete/', views.delete_sale, name='delete_sale'),  # Delete a sale

    # Walk-In Customer Sales
    path('walk-in/', views.walk_in_sale, name='walk_in_sale'),  # Handle walk-in customer sales

    # Products for Sale
    path('get-products/', views.get_products, name='get_products'),  # Fetch products for the sale

    # Sales Invoice
    path('<int:sale_id>/add-invoice/', views.add_invoice, name='add_invoice'),  # Add an invoice to a sale

    # Sale Items Management
    path('<int:sale_id>/update-items/', views.update_sale_items, name='update_sale_items'),  # Update sale items
    path('<int:sale_id>/delete-item/<int:item_id>/', views.delete_sale_item, name='delete_sale_item'),  # Delete a sale item

    # Sales Status
    path('<int:sale_id>/change-status/', views.change_sale_status, name='change_sale_status'),  # Change sales status

    # Sales Returns
    path('sales-return/create/<int:sale_id>/', views.create_sales_return, name='create_sales_return'),  # Create a sales return
    path('sales-return/list/', views.sales_return_list, name='sales_return_list'),  # List of all sales returns

    path('invoices/', views.invoice_list, name='invoice_list')
]
