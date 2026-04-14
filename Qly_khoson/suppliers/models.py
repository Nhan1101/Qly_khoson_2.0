from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


# ================= NGƯỜI DÙNG =================
class NguoiDung(AbstractUser):
    VAI_TRO_CHOICES = (
        ('Admin', 'Admin'),
        ('NhanVien', 'Nhân viên'),
    )

    vai_tro = models.CharField(max_length=50, choices=VAI_TRO_CHOICES)
    ngay_tao = models.DateTimeField(auto_now_add=True)
    dang_hoat_dong = models.BooleanField(default=True)

    def __str__(self):
        return self.username


# ================= SẢN PHẨM =================
class SanPham(models.Model):
    ma_son = models.CharField(max_length=50, unique=True)
    ten_son = models.CharField(max_length=100)
    loai_son = models.CharField(max_length=50)
    mau_sac = models.CharField(max_length=50, null=True, blank=True)
    don_vi_tinh = models.CharField(max_length=20)

    so_luong_ton = models.PositiveIntegerField(default=0)
    muc_toi_thieu = models.PositiveIntegerField(default=0)

    TINH_TRANG_CHOICES = (
        ('thieu_nhe', 'Thiếu nhẹ'),
        ('nguy_cap', 'Nguy cấp'),
    )

    tinh_trang = models.CharField(
        max_length=20,
        choices=TINH_TRANG_CHOICES,
        default='thieu_nhe'
    )

    gia_ban = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gia_nhap = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    ngay_tao = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.so_luong_ton == 0:
            self.tinh_trang = 'nguy_cap'
        else:
            self.tinh_trang = 'thieu_nhe'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ma_son} - {self.ten_son}"


# ================= NHÀ CUNG CẤP =================
class NhaCungCap(models.Model):
    ten_ncc = models.CharField(max_length=100, unique=True)
    so_dien_thoai = models.CharField(max_length=10)
    email = models.EmailField(null=True, blank=True)
    dia_chi = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.ten_ncc


# ================= ĐỐI TƯỢNG NHẬN =================
class DoiTuongNhan(models.Model):
    ten_nguoi_nhan = models.CharField(max_length=100)
    so_dien_thoai = models.CharField(max_length=10, null=True, blank=True)
    dia_chi = models.CharField(max_length=200, null=True, blank=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ten_nguoi_nhan


# ================= PHIẾU NHẬP =================
class PhieuNhap(models.Model):
    nha_cung_cap = models.ForeignKey(NhaCungCap, on_delete=models.PROTECT)
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.PROTECT)
    ngay_nhap = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Phiếu nhập {self.id}"


class ChiTietPhieuNhap(models.Model):
    phieu_nhap = models.ForeignKey(PhieuNhap, on_delete=models.CASCADE)
    san_pham = models.ForeignKey(SanPham, on_delete=models.PROTECT)

    # 🔥 BATCH
    batch_no = models.CharField(max_length=100, editable=False)
    mfg_date = models.DateField()
    exp_date = models.DateField()

    so_luong = models.PositiveIntegerField()

    class Meta:
        unique_together = ('phieu_nhap', 'batch_no')

    def generate_batch_no(self):
        today = timezone.now().strftime("%Y%m%d")
        random_code = uuid.uuid4().hex[:6].upper()
        return f"LO-{today}-{random_code}"

    def save(self, *args, **kwargs):
        with transaction.atomic():

            # tạo batch tự động
            if not self.batch_no:
                self.batch_no = self.generate_batch_no()

            # validate ngày
            if self.exp_date <= self.mfg_date:
                raise ValidationError("Hạn sử dụng phải lớn hơn ngày sản xuất!")

            san_pham = self.san_pham

            if self.pk:
                cu = ChiTietPhieuNhap.objects.get(pk=self.pk)
                san_pham.so_luong_ton -= cu.so_luong

            san_pham.so_luong_ton += self.so_luong
            san_pham.save()

            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            san_pham = self.san_pham
            san_pham.so_luong_ton -= self.so_luong
            san_pham.save()
            super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.san_pham} - {self.batch_no}"


# ================= PHIẾU XUẤT =================
class PhieuXuat(models.Model):
    doi_tuong_nhan = models.ForeignKey(DoiTuongNhan, on_delete=models.PROTECT)
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.PROTECT)
    ma_don = models.CharField(max_length=50, blank=True)
    ngay_xuat = models.DateField(auto_now_add=True)
    du_kien_giao = models.DateField(null=True, blank=True)
    ly_do_xuat = models.CharField(max_length=255, blank=True)
    tong_tien = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    da_tao_don_giao_hang = models.BooleanField(default=False)

    def __str__(self):
        return f"Phiếu xuất {self.id}"


class ChiTietPhieuXuat(models.Model):
    phieu_xuat = models.ForeignKey(PhieuXuat, on_delete=models.CASCADE)
    san_pham = models.ForeignKey(SanPham, on_delete=models.PROTECT)
    so_luong = models.PositiveIntegerField()
    don_gia = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        unique_together = ('phieu_xuat', 'san_pham')

    def save(self, *args, **kwargs):
        with transaction.atomic():
            san_pham = self.san_pham

            if self.pk:
                cu = ChiTietPhieuXuat.objects.get(pk=self.pk)
                san_pham.so_luong_ton += cu.so_luong

            if san_pham.so_luong_ton < self.so_luong:
                raise ValidationError("Không đủ số lượng tồn kho!")

            san_pham.so_luong_ton -= self.so_luong
            san_pham.save()

            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            san_pham = self.san_pham
            san_pham.so_luong_ton += self.so_luong
            san_pham.save()
            super().delete(*args, **kwargs)


# ================= PHIẾU KIỂM KÊ =================
class PhieuKiemKe(models.Model):
    TRANG_THAI_CHOICES = (
        ('draft', 'Nháp'),
        ('completed', 'Hoàn thành'),
    )

    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.PROTECT)
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, default='draft')
    ngay_tao = models.DateTimeField(auto_now_add=True)

    def cap_nhat_ton_kho(self):
        if self.trang_thai == 'completed':
            raise ValidationError("Phiếu đã hoàn thành!")

        with transaction.atomic():
            for ct in self.chitietphieukiemke_set.all():
                san_pham = ct.san_pham
                san_pham.so_luong_ton = ct.so_luong_thuc_te
                san_pham.save()

            self.trang_thai = 'completed'
            self.save()

    def __str__(self):
        return f"Phiếu kiểm kê {self.id}"


# ================= CHI TIẾT KIỂM KÊ =================
class ChiTietPhieuKiemKe(models.Model):
    phieu_kiem_ke = models.ForeignKey(PhieuKiemKe, on_delete=models.CASCADE)
    san_pham = models.ForeignKey(SanPham, on_delete=models.PROTECT)

    so_luong_he_thong = models.IntegerField()
    so_luong_thuc_te = models.IntegerField()
    chenh_lech = models.IntegerField()
    ly_do = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('phieu_kiem_ke', 'san_pham')

    def save(self, *args, **kwargs):
        self.chenh_lech = self.so_luong_thuc_te - self.so_luong_he_thong
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.san_pham} - {self.phieu_kiem_ke}"
