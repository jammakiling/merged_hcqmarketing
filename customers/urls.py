from django.urls import path
from . import views

urlpatterns = [
    path('customers/index', views.index, name='customers_index'),  # Home page that lists customers
    path('customers/<int:id>/', views.view_customer, name='view_customer'),  # View individual customers
    path('customers/add/', views.add, name='add_customer'),  # Route to add customers
    path('customers/delete/<int:id>', views.delete, name = 'delete_customer'), #delete customer
    path('customers/<int:id>/edit/', views.edit, name='customer_edit'),
]