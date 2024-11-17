from django.urls import path
from . import views

urlpatterns = [
    path('suppliers/index', views.index, name='suppliers_index'),  # Home page that lists suppliers
    path('suppliers/<int:id>/', views.view_supplier, name='view_supplier'),  # View individual supplier
    path('suppliers/add/', views.add, name='add_supplier'),  # Route to add supplier
    path('suppliers/delete/<int:id>', views.delete, name = 'delete_supplier'),
    path('suppliers/<int:id>/edit/', views.edit, name='supplier_edit'),
]