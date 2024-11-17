from django.urls import path
from . import views

urlpatterns = [
     path('sales/', views.sales_index, name='sales_index'),
    
]
