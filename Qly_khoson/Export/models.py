from django.db import models
from suppliers.models import DoiTuongNhan, NguoiDung, SanPham

class DonDatHang(models.Model):
    TRANG_THAI_CHOICES = (
        ('Chờ xử lý', 'Chờ xử lý'),
        ('Đã xuất 1 phần', 'Đã xuất 1 phần'),
        ('Đã xuất', 'Đã xuất'),
        ('Đã hủy', 'Đã hủy'),
    )

    ma_don = models.CharField(max_length=50, unique=True)
    doi_tuong_nhan = models.ForeignKey(DoiTuongNhan, on_delete=models.PROTECT, null=True, blank=True)
    ngay_dat = models.DateTimeField(auto_now_add=True)
    tong_tien = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    trang_thai = models.CharField(max_length=50, choices=TRANG_THAI_CHOICES, default='Chờ xử lý')
    ghi_chu = models.TextField(blank=True, null=True)

class ChiTietDonDatHang(models.Model):
    don_dat_hang = models.ForeignKey(DonDatHang, on_delete=models.CASCADE, related_name='details')
    san_pham = models.ForeignKey(SanPham, on_delete=models.PROTECT)
    so_luong = models.PositiveIntegerField()
    don_gia = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    thanh_tien = models.DecimalField(max_digits=15, decimal_places=2, default=0)
