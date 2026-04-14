from django.urls import path

from .views import AccountCreateView, AccountDeleteView, AccountListView, AccountUpdateView

urlpatterns = [
    path("", AccountListView.as_view(), name="taikhoan_list"),
    path("create/", AccountCreateView.as_view(), name="taikhoan_create"),
    path("<int:pk>/edit/", AccountUpdateView.as_view(), name="taikhoan_edit"),
    path("<int:pk>/delete/", AccountDeleteView.as_view(), name="taikhoan_delete"),
]
