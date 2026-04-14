from django.urls import path

from .views import KiemKeCreateView, KiemKeDetailView, KiemKeListView

urlpatterns = [
    path("", KiemKeListView.as_view(), name="kiemke_list"),
    path("create/", KiemKeCreateView.as_view(), name="kiemke_create"),
    path("<int:pk>/", KiemKeDetailView.as_view(), name="kiemke_detail"),
]
