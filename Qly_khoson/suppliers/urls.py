from django.urls import path

from .views import (
    AccountCreateView,
    AccountDeleteView,
    AccountListView,
    AccountUpdateView,
    SupplierListView,
)

urlpatterns = [
    path("", SupplierListView.as_view(), name="suppliers_list"),
    path("accounts/", AccountListView.as_view(), name="accounts_list"),
    path("accounts/create/", AccountCreateView.as_view(), name="account_create"),
    path("accounts/<int:pk>/edit/", AccountUpdateView.as_view(), name="account_edit"),
    path("accounts/<int:pk>/delete/", AccountDeleteView.as_view(), name="account_delete"),
]
