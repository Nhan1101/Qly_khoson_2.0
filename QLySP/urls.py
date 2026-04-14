from django.urls import path
from . import views

urlpatterns = [
    path('danh-muc/', views.danh_muc_sp, name='danh_muc_sp'),
    path('canh-bao-ton-kho/', views.canh_bao_ton_kho, name='canh_bao_ton_kho'),
    path('xoa-sp/<int:pk>/', views.xoa_san_pham, name='xoa_san_pham'),
    path('sua-sp/<int:pk>/', views.sua_san_pham, name='sua_sp'),
    path('canh-bao-han-su-dung/', views.canh_bao_han_su_dung, name='canh_bao_han_su_dung'),
]