from django.urls import path
from . import views

urlpatterns = [
    path('products/index', views.index, name='products_index'), 
    path('products/<int:id>/', views.view_product, name='view_product'), 
    path('products/add/', views.add, name='add_product'), 
    path('edit/<int:product_id>/', views.product_edit, name='product_edit'), 
]