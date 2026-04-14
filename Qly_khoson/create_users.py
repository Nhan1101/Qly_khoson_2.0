from suppliers.models import NguoiDung

# Kiểm tra xem đã có tài khoản chưa
count = NguoiDung.objects.count()
print(f"Số tài khoản hiện tại: {count}")

if count == 0:
    # Tạo tài khoản admin
    admin = NguoiDung.objects.create_superuser(
        username='admin',
        email='admin@alex.com',
        password='admin123',
        first_name='Admin',
        last_name='System'
    )
    print(f"✓ Tạo tài khoản admin: admin/admin123")
    
    # Tạo một số tài khoản thường
    users_data = [
        {'username': 'nhan', 'password': '123456', 'first_name': 'Nhân', 'last_name': 'Nguyễn'},
        {'username': 'thanh', 'password': '123456', 'first_name': 'Thành', 'last_name': 'Lê'},
        {'username': 'trong', 'password': '123456', 'first_name': 'Trọng', 'last_name': 'Trần'},
    ]
    
    for user_data in users_data:
        user = NguoiDung.objects.create_user(
            username=user_data['username'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=f"{user_data['username']}@alex.com",
            dang_hoat_dong=True
        )
        print(f"✓ Tạo tài khoản: {user_data['username']}/{user_data['password']}")
else:
    print("Đã có tài khoản rồi, không cần tạo")

# Hiển thị danh sách tài khoản
users = NguoiDung.objects.all()
print("\nDanh sách tài khoản hiện tại:")
for user in users:
    print(f"  - {user.username} ({user.get_full_name})")

