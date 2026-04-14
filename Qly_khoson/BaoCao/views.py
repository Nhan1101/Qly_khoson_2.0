from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone

from suppliers.models import ChiTietPhieuNhap, ChiTietPhieuXuat, PhieuNhap, PhieuXuat


def bao_cao_xuat_kho(request):
    loc_nhanh = request.GET.get("loc_nhanh", "")
    bat_dau = request.GET.get("bat_dau")
    ket_thuc = request.GET.get("ket_thuc")
    today = timezone.now().date()

    if loc_nhanh == "ngay":
        bat_dau = ket_thuc = today.strftime("%Y-%m-%d")
    elif loc_nhanh == "tuan":
        bat_dau = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        ket_thuc = today.strftime("%Y-%m-%d")
    elif loc_nhanh == "thang":
        bat_dau = today.replace(day=1).strftime("%Y-%m-%d")
        ket_thuc = today.strftime("%Y-%m-%d")
    elif loc_nhanh == "nam":
        bat_dau = today.replace(month=1, day=1).strftime("%Y-%m-%d")
        ket_thuc = today.strftime("%Y-%m-%d")

    phieu_xuat_qs = PhieuXuat.objects.all()
    if bat_dau:
        phieu_xuat_qs = phieu_xuat_qs.filter(ngay_xuat__gte=bat_dau)
    if ket_thuc:
        phieu_xuat_qs = phieu_xuat_qs.filter(ngay_xuat__lte=ket_thuc)

    tong_so_phieu = phieu_xuat_qs.count()
    tong_luong_xuat = (
        ChiTietPhieuXuat.objects.filter(phieu_xuat__in=phieu_xuat_qs).aggregate(Sum("so_luong"))["so_luong__sum"] or 0
    )

    context = {
        "tong_so_phieu": tong_so_phieu,
        "tong_luong_xuat": tong_luong_xuat,
        "danh_sach_phieu": phieu_xuat_qs.select_related("doi_tuong_nhan", "nguoi_dung").order_by("-ngay_xuat"),
        "pt_xuat": 100 if tong_luong_xuat else 0,
        "pt_hoan": 0,
        "bat_dau": bat_dau,
        "ket_thuc": ket_thuc,
        "loc_nhanh": loc_nhanh,
    }
    return render(request, "BaoCao/bao_cao_xuat_kho.html", context)


def bao_cao_nhap_kho(request):
    loc_nhanh = request.GET.get("loc_nhanh", "")
    bat_dau = request.GET.get("bat_dau")
    ket_thuc = request.GET.get("ket_thuc")
    today = timezone.now().date()

    if loc_nhanh == "ngay":
        bat_dau = ket_thuc = today.strftime("%Y-%m-%d")
    elif loc_nhanh == "tuan":
        bat_dau = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        ket_thuc = today.strftime("%Y-%m-%d")
    elif loc_nhanh == "thang":
        bat_dau = today.replace(day=1).strftime("%Y-%m-%d")
        ket_thuc = today.strftime("%Y-%m-%d")
    elif loc_nhanh == "nam":
        bat_dau = today.replace(month=1, day=1).strftime("%Y-%m-%d")
        ket_thuc = today.strftime("%Y-%m-%d")

    phieu_nhap_qs = PhieuNhap.objects.all()
    if bat_dau:
        phieu_nhap_qs = phieu_nhap_qs.filter(ngay_nhap__gte=bat_dau)
    if ket_thuc:
        phieu_nhap_qs = phieu_nhap_qs.filter(ngay_nhap__lte=ket_thuc)

    chi_tiet_qs = ChiTietPhieuNhap.objects.filter(phieu_nhap__in=phieu_nhap_qs)
    tong_luong_nhap = chi_tiet_qs.aggregate(Sum("so_luong"))["so_luong__sum"] or 0
    tong_tien_nhap = sum(ct.so_luong * ct.san_pham.gia_nhap for ct in chi_tiet_qs)

    for phieu in phieu_nhap_qs:
        phieu.tong_tien = sum(item.so_luong * item.san_pham.gia_nhap for item in phieu.chitietphieunhap_set.all())

    context = {
        "tong_so_phieu": phieu_nhap_qs.count(),
        "tong_luong_nhap": tong_luong_nhap,
        "tong_tien_nhap": tong_tien_nhap,
        "danh_sach_phieu": phieu_nhap_qs.order_by("-ngay_nhap"),
        "bat_dau": bat_dau,
        "ket_thuc": ket_thuc,
        "loc_nhanh": loc_nhanh,
    }
    return render(request, "BaoCao/bao_cao_nhap_kho.html", context)


def bao_cao_doanh_thu(request):
    loc_nhanh = request.GET.get("loc_nhanh", "")
    bat_dau = request.GET.get("bat_dau")
    ket_thuc = request.GET.get("ket_thuc")
    today = timezone.now().date()

    if loc_nhanh == "ngay":
        bat_dau = ket_thuc = today.strftime("%Y-%m-%d")
    elif loc_nhanh == "tuan":
        bat_dau = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        ket_thuc = today.strftime("%Y-%m-%d")
    elif loc_nhanh == "thang":
        bat_dau = today.replace(day=1).strftime("%Y-%m-%d")
        ket_thuc = today.strftime("%Y-%m-%d")
    elif loc_nhanh == "nam":
        bat_dau = today.replace(month=1, day=1).strftime("%Y-%m-%d")
        ket_thuc = today.strftime("%Y-%m-%d")

    phieu_xuat_qs = PhieuXuat.objects.all()
    if bat_dau:
        phieu_xuat_qs = phieu_xuat_qs.filter(ngay_xuat__gte=bat_dau)
    if ket_thuc:
        phieu_xuat_qs = phieu_xuat_qs.filter(ngay_xuat__lte=ket_thuc)

    data_theo_ngay = (
        phieu_xuat_qs.annotate(ngay=TruncDate("ngay_xuat"))
        .values("ngay")
        .annotate(so_don=Count("id", distinct=True), so_luong_sp=Sum("chitietphieuxuat__so_luong"), doanh_thu_ngay=Sum("tong_tien"))
        .order_by("-ngay")
    )

    latest_rows = list(data_theo_ngay[:10])
    chart_labels = [row["ngay"].strftime("%d/%m") for row in reversed(latest_rows)]
    chart_data = [float(row["doanh_thu_ngay"] or 0) for row in reversed(latest_rows)]

    context = {
        "tong_don_thanh_cong": phieu_xuat_qs.count(),
        "tong_doanh_thu": phieu_xuat_qs.aggregate(total=Sum("tong_tien"))["total"] or 0,
        "data_theo_ngay": data_theo_ngay,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "bat_dau": bat_dau,
        "ket_thuc": ket_thuc,
        "loc_nhanh": loc_nhanh,
    }
    return render(request, "BaoCao/bao_cao_doanh_thu.html", context)
