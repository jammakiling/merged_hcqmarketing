from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_index, name='inventory_index'),  # URL for inventory index page
    path('<int:product_id>/', views.product_detail, name='product_detail'),
]