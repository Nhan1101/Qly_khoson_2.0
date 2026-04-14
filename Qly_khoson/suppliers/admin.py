from django.contrib import admin

from .models import (
    ChiTietPhieuKiemKe,
    ChiTietPhieuNhap,
    ChiTietPhieuXuat,
    DoiTuongNhan,
    NguoiDung,
    NhaCungCap,
    PhieuKiemKe,
    PhieuNhap,
    PhieuXuat,
    SanPham,
    TonKho,
)

admin.site.register(NguoiDung)
admin.site.register(NhaCungCap)
admin.site.register(SanPham)
admin.site.register(TonKho)
admin.site.register(DoiTuongNhan)
admin.site.register(PhieuNhap)
admin.site.register(ChiTietPhieuNhap)
admin.site.register(PhieuXuat)
admin.site.register(ChiTietPhieuXuat)
admin.site.register(PhieuKiemKe)
admin.site.register(ChiTietPhieuKiemKe)

