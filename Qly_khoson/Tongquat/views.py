from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from suppliers.models import PhieuXuat


@login_required
def index(request):
    query = request.GET.get("ma_don_hang")
    don_hang = None
    error_message = None

    if query:
        don_hang = PhieuXuat.objects.filter(id=query).first()
        if not don_hang:
            error_message = "Đơn hàng không tồn tại"

    return render(
        request,
        "trangchu.html",
        {"don_hang": don_hang, "error_message": error_message, "query": query},
    )
