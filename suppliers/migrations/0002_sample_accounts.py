from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_sample_accounts(apps, schema_editor):
    NguoiDung = apps.get_model("suppliers", "NguoiDung")

    sample_accounts = [
        {"username": "NV001", "first_name": "Lê Thị", "last_name": "Thanh", "vai_tro": "Admin", "password": "lethanh1205"},
        {"username": "NV002", "first_name": "Nguyễn Trần", "last_name": "Nhân", "vai_tro": "NhanVien", "password": "Nhan@1101"},
        {"username": "NV003", "first_name": "Bùi Quỳnh", "last_name": "Như", "vai_tro": "NhanVien", "password": "12345"},
        {"username": "NV004", "first_name": "Trần Thị", "last_name": "Thúy Trâm", "vai_tro": "NhanVien", "password": "13572468"},
        {"username": "NV005", "first_name": "Nguyễn Tường", "last_name": "Vy", "vai_tro": "NhanVien", "password": "Vy1234"},
        {"username": "NV006", "first_name": "Nguyễn Văn", "last_name": "A", "vai_tro": "NhanVien", "password": "12345"},
        {"username": "NV007", "first_name": "Nguyễn Văn", "last_name": "B", "vai_tro": "NhanVien", "password": "12345"},
        {"username": "NV008", "first_name": "Nguyễn Trần", "last_name": "Nghĩa", "vai_tro": "NhanVien", "password": "A13579"},
        {"username": "NV009", "first_name": "Đoàn Xuân", "last_name": "Toàn", "vai_tro": "GiaoHang", "password": "123456"},
        {"username": "NV010", "first_name": "Nguyễn Nhật", "last_name": "Hạ", "vai_tro": "GiaoHang", "password": "123456"},
        {"username": "NV011", "first_name": "Nguyễn Thị", "last_name": "Giang", "vai_tro": "GiaoHang", "password": "Nhan1101"},
        {"username": "NV012", "first_name": "Nguyễn Văn", "last_name": "D", "vai_tro": "GiaoHang", "password": "Nhann13257"},
        {"username": "NV013", "first_name": "Phạm Văn", "last_name": "E", "vai_tro": "GiaoHang", "password": "PhamE123"},
        {"username": "NV014", "first_name": "Hoàng Thị", "last_name": "F", "vai_tro": "GiaoHang", "password": "HoangF456"},
        {"username": "NV015", "first_name": "Đỗ Văn", "last_name": "G", "vai_tro": "GiaoHang", "password": "DoG789"},
    ]

    for account in sample_accounts:
        user, created = NguoiDung.objects.get_or_create(
            username=account["username"],
            defaults={
                "first_name": account["first_name"],
                "last_name": account["last_name"],
                "vai_tro": account["vai_tro"],
                "is_active": True,
                "password": make_password(account["password"]),
            },
        )


def delete_sample_accounts(apps, schema_editor):
    NguoiDung = apps.get_model("suppliers", "NguoiDung")
    usernames = [
        "NV001",
        "NV002",
        "NV003",
        "NV004",
        "NV005",
        "NV006",
        "NV007",
        "NV008",
        "NV009",
        "NV010",
        "NV011",
        "NV012",
        "NV013",
        "NV014",
        "NV015",
    ]
    NguoiDung.objects.filter(username__in=usernames).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("suppliers", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_sample_accounts, reverse_code=delete_sample_accounts),
    ]
