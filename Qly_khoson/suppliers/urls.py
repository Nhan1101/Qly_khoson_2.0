from django.urls import path

from .views import (
    SupplierListView,
    supplier_create,
    supplier_delete,
    supplier_update,
)

urlpatterns = [
    path("", SupplierListView.as_view(), name="suppliers_list"),
    path("create/", supplier_create, name="supplier_create"),
    path("<int:pk>/update/", supplier_update, name="supplier_update"),
    path("<int:pk>/delete/", supplier_delete, name="supplier_delete"),
]
