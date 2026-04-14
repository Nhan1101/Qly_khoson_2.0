from django.shortcuts import render
from django.views.generic import TemplateView
from suppliers.models import NhaCungCap

# Màn hình chọn thao tác Nhập kho (Thay vì hiện danh sách ngay)
class NhapKhoHomeView(TemplateView):
    template_name = 'nhapkho/nhap_kho_home.html'

# Nhập kho
class NhapKhoListView(TemplateView):
    template_name = 'nhapkho/nhapkho.html'

class TaoPhieuNhapView(TemplateView):
    template_name = 'nhapkho/taophieunhap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nhacungcaps'] = NhaCungCap.objects.all()
        return context

class SuaPhieuNhapView(TemplateView):
    template_name = 'nhapkho/suaphieunhap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nhacungcaps'] = NhaCungCap.objects.all()
        return context

class XemPhieuView(TemplateView):
    template_name = 'nhapkho/xemctphieu.html'

# Đơn đặt hàng
class DsDonDatHangNccView(TemplateView):
    template_name = 'nhapkho/dsddh.html'

class ChiTietDonDatHangView(TemplateView):
    template_name = 'nhapkho/ctddh.html'

class TaoDonDatHangView(TemplateView):
    template_name = 'nhapkho/taodondathang.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nhacungcaps'] = NhaCungCap.objects.all()
        return context

class SuaDonDatHangView(TemplateView):
    template_name = 'nhapkho/suadondathang.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nhacungcaps'] = NhaCungCap.objects.all()
        return context

class DanhSachNccView(TemplateView):
    template_name = 'nhapkho/dsncc.html'
