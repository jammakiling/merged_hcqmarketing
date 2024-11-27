from django.urls import path
from . import views

urlpatterns = [
    path('sales/index', views.index, name='sales_index'),
    path('sales/add/', views.add, name='new_sales_order_add'),
]

