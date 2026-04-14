from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models, transaction


class NguoiDung(AbstractUser):
    VAI_TRO_CHOICES = (
        ("Admin", "Admin"),
        ("NhanVien", "NhanVien"),
    )

    vai_tro = models.CharField(max_length=50, choices=VAI_TRO_CHOICES)
    ngay_tao = models.DateTimeField(auto_now_add=True)
    dang_hoat_dong = models.BooleanField(default=True)

    def __str__(self):
        return self.username


class SanPham(models.Model):
    ma_son = models.CharField(max_length=50, unique=True)
    ten_son = models.CharField(max_length=100)
    loai_son = models.CharField(max_length=50)
    mau_sac = models.CharField(max_length=50, null=True, blank=True)
    don_vi_tinh = models.CharField(max_length=20)
    so_luong_ton = models.IntegerField(default=0)
    gia_ban = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gia_nhap = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    han_su_dung = models.DateField(null=True, blank=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ma_son} - {self.ten_son}"

    @property
    def muc_toi_thieu(self):
        ton_kho = getattr(self, "tonkho", None)
        return ton_kho.muc_toi_thieu if ton_kho else 0


class NhaCungCap(models.Model):
    ten_ncc = models.CharField(max_length=100, unique=True)
    so_dien_thoai = models.CharField(max_length=10)
    email = models.EmailField(max_length=254, null=True, blank=True)
    dia_chi = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.ten_ncc

    @property
    def ma_ncc(self):
        if self.pk is None:
            return "NCC_00"
        return f"NCC_{self.pk:02d}"


class DoiTuongNhan(models.Model):
    ten_nguoi_nhan = models.CharField(max_length=100)
    so_dien_thoai = models.CharField(max_length=10, null=True, blank=True)
    dia_chi = models.CharField(max_length=200, null=True, blank=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ten_nguoi_nhan


class TonKho(models.Model):
    TINH_TRANG_CHOICES = (
        ("thieu_nhe", "Thieu nhe"),
        ("nguy_cap", "Nguy cap"),
    )

    san_pham = models.OneToOneField(SanPham, on_delete=models.CASCADE)
    so_luong_ton = models.PositiveIntegerField(default=0)
    muc_toi_thieu = models.PositiveIntegerField(default=0)
    tinh_trang = models.CharField(
        max_length=20,
        choices=TINH_TRANG_CHOICES,
        default="thieu_nhe",
    )

    def save(self, *args, **kwargs):
        self.tinh_trang = "nguy_cap" if self.so_luong_ton <= self.muc_toi_thieu else "thieu_nhe"
        super().save(*args, **kwargs)


class PhieuNhap(models.Model):
    nha_cung_cap = models.ForeignKey(NhaCungCap, on_delete=models.PROTECT)
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.PROTECT)
    ngay_nhap = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Phieu nhap {self.pk}"


class ChiTietPhieuNhap(models.Model):
    phieu_nhap = models.ForeignKey(PhieuNhap, on_delete=models.CASCADE)
    san_pham = models.ForeignKey(SanPham, on_delete=models.PROTECT)
    so_luong = models.PositiveIntegerField()

    class Meta:
        unique_together = ("phieu_nhap", "san_pham")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            ton_kho, _ = TonKho.objects.get_or_create(san_pham=self.san_pham)
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


class PhieuXuat(models.Model):
    doi_tuong_nhan = models.ForeignKey(DoiTuongNhan, on_delete=models.PROTECT)
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.PROTECT)
    ngay_xuat = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Phieu xuat {self.pk}"


class ChiTietPhieuXuat(models.Model):
    phieu_xuat = models.ForeignKey(PhieuXuat, on_delete=models.CASCADE)
    san_pham = models.ForeignKey(SanPham, on_delete=models.PROTECT)
    so_luong = models.PositiveIntegerField()

    class Meta:
        unique_together = ("phieu_xuat", "san_pham")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            ton_kho = TonKho.objects.get(san_pham=self.san_pham)
            if self.pk:
                cu = ChiTietPhieuXuat.objects.get(pk=self.pk)
                ton_kho.so_luong_ton += cu.so_luong
            if ton_kho.so_luong_ton < self.so_luong:
                raise ValidationError("Khong du so luong ton kho.")
            ton_kho.so_luong_ton -= self.so_luong
            ton_kho.save()
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            ton_kho = TonKho.objects.get(san_pham=self.san_pham)
            ton_kho.so_luong_ton += self.so_luong
            ton_kho.save()
            super().delete(*args, **kwargs)


class PhieuKiemKe(models.Model):
    TRANG_THAI_CHOICES = (
        ("draft", "Nhap"),
        ("completed", "Hoan thanh"),
    )

    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.PROTECT)
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, default="draft")
    ngay_tao = models.DateTimeField(auto_now_add=True)

    def cap_nhat_ton_kho(self):
        if self.trang_thai == "completed":
            raise ValidationError("Phieu da hoan thanh.")

        with transaction.atomic():
            for chi_tiet in self.chitietphieukiemke_set.all():
                ton_kho, _ = TonKho.objects.get_or_create(san_pham=chi_tiet.san_pham)
                ton_kho.so_luong_ton = chi_tiet.so_luong_thuc_te
                ton_kho.save()

            self.trang_thai = "completed"
            self.save(update_fields=["trang_thai"])

    def __str__(self):
        return f"Phieu kiem ke {self.pk}"


class ChiTietPhieuKiemKe(models.Model):
    phieu_kiem_ke = models.ForeignKey(PhieuKiemKe, on_delete=models.CASCADE)
    san_pham = models.ForeignKey(SanPham, on_delete=models.PROTECT)
    so_luong_he_thong = models.IntegerField()
    so_luong_thuc_te = models.IntegerField()
    chenh_lech = models.IntegerField()
    ly_do = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ("phieu_kiem_ke", "san_pham")

    def save(self, *args, **kwargs):
        self.chenh_lech = self.so_luong_thuc_te - self.so_luong_he_thong
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.san_pham} - {self.phieu_kiem_ke}"

