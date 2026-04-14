from django.urls import path
from .views import (
    NhapKhoListView, TaoPhieuNhapView, SuaPhieuNhapView, XemPhieuView,
    DsDonDatHangNccView, ChiTietDonDatHangView, TaoDonDatHangView, DanhSachNccView
)

urlpatterns = [
    # Nhập kho
    path('nhap-kho/', NhapKhoListView.as_view(), name='nhap_kho'),
    path('nhap-kho/tao/', TaoPhieuNhapView.as_view(), name='tao_phieu_nhap'),
    path('nhap-kho/sua/', SuaPhieuNhapView.as_view(), name='sua_phieu_nhap'),
    path('nhap-kho/xem/', XemPhieuView.as_view(), name='xem_phieu'),

    # Đơn đặt hàng
    path('don-dat-hang-ncc/', DsDonDatHangNccView.as_view(), name='ds_don_dat_hang_ncc'),
    path('don-dat-hang-ncc/tao/', TaoDonDatHangView.as_view(), name='tao_don_dat_hang'),
    path('don-dat-hang-ncc/chi-tiet/', ChiTietDonDatHangView.as_view(), name='chi_tiet_don_dat_hang'),
    path('don-dat-hang-ncc/nha-cung-cap/', DanhSachNccView.as_view(), name='danh_sach_ncc'),
]
