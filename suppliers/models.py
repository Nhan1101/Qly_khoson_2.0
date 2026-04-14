from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import datetime

# ================= NGƯỜI DÙNG =================
class NguoiDung(AbstractUser):
    VAI_TRO_CHOICES = (
        ('Admin', 'Chủ cửa hàng'),
        ('NhanVien', 'Nhân viên kho'),
        ('GiaoHang', 'Giao hàng'),
    )

    vai_tro = models.CharField(max_length=50, choices=VAI_TRO_CHOICES)
    ngay_tao = models.DateTimeField(auto_now_add=True)
    dang_hoat_dong = models.BooleanField(default=True)

    def __str__(self):
        return self.username


# ================= SẢN PHẨM =================
class SanPham(models.Model):
    ma_son = models.CharField(max_length=50, unique=True, blank=True)
    ten_son = models.CharField(max_length=100)
    loai_son = models.CharField(max_length=50)
    mau_sac = models.CharField(max_length=50, null=True, blank=True)
    don_vi_tinh = models.CharField(max_length=20)

    so_luong_ton = models.IntegerField(default=0)
    gia_nhap = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    ty_le_loi_nhuan = models.FloatField(default=0)  # Ví dụ: 20 tương đương 20%
    gia_ban = models.DecimalField(max_digits=15, decimal_places=2, default=0, editable=False)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # 1. Tự động sinh mã hàng hóa nếu chưa có
        if not self.ma_son:
            prefix = f"SON-{datetime.datetime.now().strftime('%y%m')}-"
            last_sp = SanPham.objects.filter(ma_son__startswith=prefix).order_by('-ma_son').first()
            if last_sp:
                last_no = int(last_sp.ma_son.split('-')[-1])
                new_no = str(last_no + 1).zfill(4)
            else:
                new_no = '0001'
            self.ma_son = f"{prefix}{new_no}"

        # 2. Tự động tính giá bán
        loi_nhuan = float(self.gia_nhap) * (self.ty_le_loi_nhuan / 100)
        self.gia_ban = float(self.gia_nhap) + loi_nhuan

        super(SanPham, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.ma_son} - {self.ten_son}"


# ================= NHÀ CUNG CẤP =================
class NhaCungCap(models.Model):
    ten_ncc = models.CharField(max_length=100, unique=True)
    so_dien_thoai = models.CharField(max_length=10)
    email = models.EmailField(max_length=254, null=True, blank=True)
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


# ================= TỒN KHO =================
class TonKho(models.Model):
    TINH_TRANG_CHOICES = (
        ('thieu_nhe', 'Thiếu nhẹ'),
        ('nguy_cap', 'Nguy cấp'),
    )

    san_pham = models.OneToOneField(SanPham, on_delete=models.CASCADE)
    so_luong_ton = models.PositiveIntegerField(default=0)
    muc_toi_thieu = models.PositiveIntegerField(default=0)
    tinh_trang = models.CharField(max_length=20, choices=TINH_TRANG_CHOICES, default='thieu_nhe')

    def save(self, *args, **kwargs):
        if self.so_luong_ton <= self.muc_toi_thieu:
            self.tinh_trang = 'nguy_cap'
        else:
            self.tinh_trang = 'thieu_nhe'
        super().save(*args, **kwargs)


# ================= PHIẾU NHẬP & CHI TIẾT =================
class PhieuNhap(models.Model):
    nha_cung_cap = models.ForeignKey(NhaCungCap, on_delete=models.PROTECT)
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.PROTECT)
    ngay_nhap = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Phiếu nhập {self.id} - {self.ngay_nhap}"


class ChiTietPhieuNhap(models.Model):
    phieu_nhap = models.ForeignKey(PhieuNhap, on_delete=models.CASCADE, related_name='chi_tiet')
    san_pham = models.ForeignKey(SanPham, on_delete=models.PROTECT)
    so_luong = models.PositiveIntegerField()
    # THÊM MÃ LÔ VÀ HSD VÀO ĐÂY
    ma_lo = models.CharField(max_length=50, blank=True)
    han_su_dung = models.DateField()

    class Meta:
        unique_together = ('phieu_nhap', 'san_pham')

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Tự động tạo mã lô nếu chưa có: LO-[NămTháng]-[ID Sản phẩm]
            if not self.ma_lo:
                self.ma_lo = f"LO-{datetime.datetime.now().strftime('%y%m')}-{self.san_pham.id}"

            ton_kho, created = TonKho.objects.get_or_create(san_pham=self.san_pham)

            if self.pk:
                cu = ChiTietPhieuNhap.objects.get(pk=self.pk)
                ton_kho.so_luong_ton -= cu.so_luong

            ton_kho.so_luong_ton += self.so_luong
            ton_kho.save()

            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            ton_kho = TonKho.objects.get(san_pham=self.san_pham)
            ton_kho.so_luong_ton -= self.so_luong
            ton_kho.save()
            super().delete(*args, **kwargs)


# ================= PHIẾU XUẤT & CHI TIẾT =================
class PhieuXuat(models.Model):
    doi_tuong_nhan = models.ForeignKey(DoiTuongNhan, on_delete=models.PROTECT)
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.PROTECT)
    ngay_xuat = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Phiếu xuất {self.id}"


class ChiTietPhieuXuat(models.Model):
    phieu_xuat = models.ForeignKey(PhieuXuat, on_delete=models.CASCADE)
    san_pham = models.ForeignKey(SanPham, on_delete=models.PROTECT)
    so_luong = models.PositiveIntegerField()

    class Meta:
        unique_together = ('phieu_xuat', 'san_pham')

    def save(self, *args, **kwargs):
        with transaction.atomic():
            ton_kho = TonKho.objects.get(san_pham=self.san_pham)

            if self.pk:
                cu = ChiTietPhieuXuat.objects.get(pk=self.pk)
                ton_kho.so_luong_ton += cu.so_luong

            if ton_kho.so_luong_ton < self.so_luong:
                raise ValidationError(f"Không đủ tồn kho cho {self.san_pham.ten_son}!")

            ton_kho.so_luong_ton -= self.so_luong
            ton_kho.save()
            super().save(*args, **kwargs)


# ================= KIỂM KÊ =================
class PhieuKiemKe(models.Model):
    TRANG_THAI_CHOICES = (('draft', 'Nháp'), ('completed', 'Hoàn thành'))
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.PROTECT)
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, default='draft')
    ngay_tao = models.DateTimeField(auto_now_add=True)

    def cap_nhat_ton_kho(self):
        if self.trang_thai == 'completed':
            raise ValidationError("Phiếu đã hoàn thành!")
        with transaction.atomic():
            for ct in self.chitietphieukiemke_set.all():
                ton_kho, _ = TonKho.objects.get_or_create(san_pham=ct.san_pham)
                ton_kho.so_luong_ton = ct.so_luong_thuc_te
                ton_kho.save()
            self.trang_thai = 'completed'
            self.save()


class ChiTietPhieuKiemKe(models.Model):
    phieu_kiem_ke = models.ForeignKey(PhieuKiemKe, on_delete=models.CASCADE)
    san_pham = models.ForeignKey(SanPham, on_delete=models.PROTECT)
    so_luong_he_thong = models.IntegerField()
    so_luong_thuc_te = models.IntegerField()
    chenh_lech = models.IntegerField(editable=False)
    ly_do = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('phieu_kiem_ke', 'san_pham')

    def save(self, *args, **kwargs):
        self.chenh_lech = self.so_luong_thuc_te - self.so_luong_he_thong
        super().save(*args, **kwargs)


class LichSuDonHang(models.Model):
    TRANG_THAI_VAN_DON = (
        ('tao_don', 'Tạo đơn hàng'),
        ('xuat_kho', 'Xuất kho'),
        ('dang_giao', 'Đang giao hàng'),
        ('thanh_cong', 'Giao hàng thành công'),
    )
    phieu_xuat = models.ForeignKey(PhieuXuat, on_delete=models.CASCADE, related_name='lich_su')
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_VAN_DON)
    thoi_gian = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-thoi_gian']