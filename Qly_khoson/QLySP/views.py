from datetime import timedelta

from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from suppliers.models import ChiTietPhieuNhap, SanPham

from .forms import SanPhamForm


def danh_muc_sp(request):
    if request.method == "POST":
        form = SanPhamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("danh_muc_sp")
    else:
        form = SanPhamForm()

    products = SanPham.objects.all().order_by("-ngay_tao")
    ma_hang = request.GET.get("ma_hang", "")
    ten_hang = request.GET.get("ten_hang", "")

    if ma_hang:
        products = products.filter(ma_son__icontains=ma_hang)
    if ten_hang:
        products = products.filter(ten_son__icontains=ten_hang)

    return render(
        request,
        "danhmuc.html",
        {"products": products, "form": form, "ma_hang": ma_hang, "ten_hang": ten_hang},
    )


def sua_san_pham(request, pk):
    san_pham = get_object_or_404(SanPham, pk=pk)
    if request.method == "POST":
        form = SanPhamForm(request.POST, instance=san_pham)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success"})
        return JsonResponse({"status": "error", "errors": form.errors})
    return JsonResponse({"status": "error", "message": "Yêu cầu không hợp lệ"})


def xoa_san_pham(request, pk):
    get_object_or_404(SanPham, pk=pk).delete()
    return redirect("danh_muc_sp")


def canh_bao_ton_kho(request):
    danh_sach_canh_bao = SanPham.objects.filter(so_luong_ton__lte=F("muc_toi_thieu")).order_by("so_luong_ton", "id")
    return render(request, "canhbao.html", {"danh_sach_canh_bao": danh_sach_canh_bao})


def canh_bao_han_su_dung(request):
    ngay_hien_tai = timezone.now().date()
    moc_canh_bao = ngay_hien_tai + timedelta(days=15)

    lo_sap_het_han = (
        ChiTietPhieuNhap.objects.filter(exp_date__lte=moc_canh_bao, exp_date__gte=ngay_hien_tai)
        .select_related("san_pham")
        .order_by("exp_date")
    )

    for lo in lo_sap_het_han:
        lo.so_ngay_con_lai = (lo.exp_date - ngay_hien_tai).days

    return render(
        request,
        "canh_bao_hsd.html",
        {"lo_sap_het_han": lo_sap_het_han, "ngay_hien_tai": ngay_hien_tai},
    )
