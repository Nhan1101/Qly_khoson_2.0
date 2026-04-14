from django.core.management.base import BaseCommand
from suppliers.models import NguoiDung, SanPham, NhaCungCap, DoiTuongNhan

class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu ban đầu nếu hệ thống chưa có dữ liệu'

    def handle(self, *args, **kwargs):
        if SanPham.objects.exists():
            self.stdout.write(self.style.WARNING("Dữ liệu đã tồn tại, không thực hiện seed."))
            return
        
        self.stdout.write(self.style.SUCCESS("Đang khởi tạo dữ liệu mẫu..."))
        
        # Tạo Admin
        admin, created = NguoiDung.objects.get_or_create(username="admin", defaults={
            "email": "admin@alex.com",
            "vai_tro": "Admin"
        })
        if created:
            admin.set_password("admin123")
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
            
        nhanvien, created = NguoiDung.objects.get_or_create(username="nhanvien", defaults={
            "email": "nv@alex.com",
            "vai_tro": "NhanVien"
        })
        if created:
            nhanvien.set_password("123456")
            nhanvien.save()

        # Tạo Nhà Cung Cấp
        ncc1 = NhaCungCap.objects.create(ten_ncc='NPP Sơn Alex MB', so_dien_thoai='0123456781', email='mb@alex.com', dia_chi='Hà Nội')
        ncc2 = NhaCungCap.objects.create(ten_ncc='NPP Sơn Alex MN', so_dien_thoai='0123456782', email='mn@alex.com', dia_chi='Hồ Chí Minh')

        # Tạo Đối tượng nhận
        dt1 = DoiTuongNhan.objects.create(ten_nguoi_nhan='Cửa hàng đại lý A', so_dien_thoai='0909000111', dia_chi='Hải Phòng')

        # Tạo Sản Phẩm
        products = [
            {"ma_son": "ALEX01", "ten_son": "Sơn ngoại thất Alex", "loai_son": "Ngoại thất", "mau_sac": "Trắng", "don_vi_tinh": "Thùng 18L", "gia_nhap": 1200000, "gia_ban": 1500000, "ton": 50},
            {"ma_son": "ALEX02", "ten_son": "Sơn nội thất Alex", "loai_son": "Nội thất", "mau_sac": "Kem", "don_vi_tinh": "Lon 5L", "gia_nhap": 300000, "gia_ban": 450000, "ton": 100},
            {"ma_son": "ALEX03", "ten_son": "Sơn chống thấm Alex", "loai_son": "Chống thấm", "mau_sac": "Ghi", "don_vi_tinh": "Thùng 18L", "gia_nhap": 1500000, "gia_ban": 1800000, "ton": 20},
        ]

        for p in products:
            sp = SanPham.objects.create(
                ma_son=p["ma_son"],
                ten_son=p["ten_son"],
                loai_son=p["loai_son"],
                mau_sac=p["mau_sac"],
                don_vi_tinh=p["don_vi_tinh"],
                gia_nhap=p["gia_nhap"],
                gia_ban=p["gia_ban"]
            )
            sp.so_luong_ton = p["ton"]
            sp.save()

        # Tạo đơn đặt hàng mẫu
        from Export.models import DonDatHang, ChiTietDonDatHang
        if not DonDatHang.objects.exists():
            dh = DonDatHang.objects.create(
                ma_don="DH0001",
                doi_tuong_nhan=dt1,
                tong_tien=3000000,
                trang_thai="Chờ xử lý"
            )
            sp1 = SanPham.objects.first()
            if sp1:
                ChiTietDonDatHang.objects.create(
                    don_dat_hang=dh,
                    san_pham=sp1,
                    so_luong=2,
                    don_gia=sp1.gia_ban,
                    thanh_tien=sp1.gia_ban * 2
                )

        self.stdout.write(self.style.SUCCESS("Đã seed dữ liệu thành công!"))
