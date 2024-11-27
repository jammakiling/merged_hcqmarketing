from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    path('purchases/', views.purchase_index, name='purchase_index'),
    path('add/', views.add_purchase, name='add_purchase'),
    path('change_status/<int:id>/', views.change_purchase_status, name='change_purchase_status'),
    path('<int:purchase_id>/', views.purchase_detail, name='purchase_detail'),
    path('<int:purchase_id>/add_invoice/', views.add_invoice, name='add_invoice'),
    path('returns/', views.purchase_return_list, name='purchase_return_list'),
    path('returns/create/', views.create_purchase_return, name='create_purchase_return'),
]