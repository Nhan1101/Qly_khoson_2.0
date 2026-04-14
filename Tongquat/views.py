from django.shortcuts import render
from suppliers.models import PhieuXuat
# Create your views here.

def index(request):
    return render(request, 'trangchu.html')

def index(request):
    query = request.GET.get('ma_don_hang')  # Lấy mã từ ô input (name="ma_don_hang")
    don_hang = None
    error_message = None

    if query:
        # Tìm kiếm phiếu xuất theo ID hoặc số điện thoại người nhận
        don_hang = PhieuXuat.objects.filter(id=query).first()

        if not don_hang:
            error_message = "Đơn hàng không tồn tại"

    return render(request, 'trangchu.html', {
        'don_hang': don_hang,
        'error_message': error_message,
        'query': query
    })