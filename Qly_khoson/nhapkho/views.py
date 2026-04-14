from django.shortcuts import render
from django.views.generic import TemplateView

# Nhập kho
class NhapKhoListView(TemplateView):
    template_name = 'nhapkho/nhapkho.html'

class TaoPhieuNhapView(TemplateView):
    template_name = 'nhapkho/taophieunhap.html'

class SuaPhieuNhapView(TemplateView):
    template_name = 'nhapkho/suaphieunhap.html'

class XemPhieuView(TemplateView):
    template_name = 'nhapkho/xemctphieu.html'

# Đơn đặt hàng
class DsDonDatHangNccView(TemplateView):
    template_name = 'nhapkho/dsddh.html'

class ChiTietDonDatHangView(TemplateView):
    template_name = 'nhapkho/ctddh.html'

class TaoDonDatHangView(TemplateView):
    template_name = 'nhapkho/taodondathang.html'

class DanhSachNccView(TemplateView):
    template_name = 'nhapkho/dsncc.html'
