from django.urls import path
from . import views

urlpatterns = [
    path('xuat-kho/', views.bao_cao_xuat_kho, name='bao_cao_xuat_kho'),
    path('nhap-kho/', views.bao_cao_nhap_kho, name='bao_cao_nhap_kho'),
    path('doanh-thu/', views.bao_cao_doanh_thu, name='bao_cao_doanh_thu'),
]