from django.shortcuts import render
from suppliers.models import PhieuXuat, ChiTietPhieuXuat, PhieuNhap, ChiTietPhieuNhap, LichSuDonHang
from django.db.models import Sum,Count,F
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDate


def bao_cao_xuat_kho(request):
    # 1. Lấy tham số lọc từ URL
    loc_nhanh = request.GET.get('loc_nhanh', '')
    bat_dau = request.GET.get('bat_dau')
    ket_thuc = request.GET.get('ket_thuc')

    today = timezone.now().date()

    # 2. Xử lý logic Lọc nhanh (Ngày, Tuần, Tháng, Năm)
    if loc_nhanh == 'ngay':
        bat_dau = ket_thuc = today.strftime('%Y-%m-%d')
    elif loc_nhanh == 'tuan':
        # Tính từ thứ 2 đến Chủ nhật của tuần hiện tại
        bat_dau = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
        ket_thuc = today.strftime('%Y-%m-%d')
    elif loc_nhanh == 'thang':
        # Tính từ ngày 1 của tháng hiện tại
        bat_dau = today.replace(day=1).strftime('%Y-%m-%d')
        ket_thuc = today.strftime('%Y-%m-%d')
    elif loc_nhanh == 'nam':
        # Tính từ ngày 1/1 của năm hiện tại
        bat_dau = today.replace(month=1, day=1).strftime('%Y-%m-%d')
        ket_thuc = today.strftime('%Y-%m-%d')

    # 3. Truy vấn dữ liệu gốc
    phi_eu_xuat_qs = PhieuXuat.objects.all()

    # Áp dụng bộ lọc ngày nếu có
    if bat_dau:
        phi_eu_xuat_qs = phi_eu_xuat_qs.filter(ngay_xuat__gte=bat_dau)
    if ket_thuc:
        phi_eu_xuat_qs = phi_eu_xuat_qs.filter(ngay_xuat__lte=ket_thuc)

    # 4. Tính toán các con số thống kê cho thẻ (Cards)
    tong_so_phieu = phi_eu_xuat_qs.count()
    tong_luong_xuat = ChiTietPhieuXuat.objects.filter(
        phieu_xuat__in=phi_eu_xuat_qs
    ).aggregate(Sum('so_luong'))['so_luong__sum'] or 0

    # 5. Tính toán tỉ lệ cho biểu đồ (Chart)
    tong_xuat_kh = tong_luong_xuat
    tong_hoan_hang = 0  # Bạn có thể thêm model HoanHang để lấy dữ liệu thực tế tại đây

    tong_cong = tong_xuat_kh + tong_hoan_hang

    # Tính % (Nếu không có dữ liệu sẽ trả về 0 thay vì số giả lập 81-19)
    pt_xuat = round((tong_xuat_kh / tong_cong * 100), 1) if tong_cong > 0 else 0
    pt_hoan = round((tong_hoan_hang / tong_cong * 100), 1) if tong_cong > 0 else 0

    # 6. Danh sách phiếu hiển thị ở bảng bên dưới
    danh_sach_phieu = phi_eu_xuat_qs.select_related('doi_tuong_nhan', 'nguoi_dung').order_by('-ngay_xuat')

    context = {
        'tong_so_phieu': tong_so_phieu,
        'tong_luong_xuat': tong_luong_xuat,
        'danh_sach_phieu': danh_sach_phieu,
        'pt_xuat': pt_xuat,
        'pt_hoan': pt_hoan,
        'bat_dau': bat_dau,
        'ket_thuc': ket_thuc,
        'loc_nhanh': loc_nhanh,
    }

    return render(request, 'BaoCao/bao_cao_xuat_kho.html', context)


def bao_cao_nhap_kho(request):
    loc_nhanh = request.GET.get('loc_nhanh', '')
    bat_dau = request.GET.get('bat_dau')
    ket_thuc = request.GET.get('ket_thuc')
    today = timezone.now().date()

    if loc_nhanh == 'ngay':
        bat_dau = ket_thuc = today.strftime('%Y-%m-%d')
    elif loc_nhanh == 'tuan':
        bat_dau = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
        ket_thuc = today.strftime('%Y-%m-%d')
    elif loc_nhanh == 'thang':
        bat_dau = today.replace(day=1).strftime('%Y-%m-%d')
        ket_thuc = today.strftime('%Y-%m-%d')
    elif loc_nhanh == 'nam':
        bat_dau = today.replace(month=1, day=1).strftime('%Y-%m-%d')
        ket_thuc = today.strftime('%Y-%m-%d')

    phi_eu_nhap_qs = PhieuNhap.objects.all()
    if bat_dau:
        phi_eu_nhap_qs = phi_eu_nhap_qs.filter(ngay_nhap__gte=bat_dau)
    if ket_thuc:
        phi_eu_nhap_qs = phi_eu_nhap_qs.filter(ngay_nhap__lte=ket_thuc)

    tong_so_phieu = phi_eu_nhap_qs.count()

    # Lấy chi tiết để tính tổng lượng và tổng tiền
    chi_tiet_qs = ChiTietPhieuNhap.objects.filter(phieu_nhap__in=phi_eu_nhap_qs)
    tong_luong_nhap = chi_tiet_qs.aggregate(Sum('so_luong'))['so_luong__sum'] or 0

    # Tính tổng tiền = sum(so_luong * gia_nhap)
    tong_tien_nhap = 0
    for ct in chi_tiet_qs:
        tong_tien_nhap += ct.so_luong * ct.san_pham.gia_nhap

    # Danh sách hiển thị bảng (tính tổng tiền cho từng phiếu)
    for p in phi_eu_nhap_qs:
        p.tong_tien = sum(item.so_luong * item.san_pham.gia_nhap for item in p.chi_tiet.all())

    context = {
        'tong_so_phieu': tong_so_phieu,
        'tong_luong_nhap': tong_luong_nhap,
        'tong_tien_nhap': tong_tien_nhap,
        'danh_sach_phieu': phi_eu_nhap_qs.order_by('-ngay_nhap'),
        'bat_dau': bat_dau,
        'ket_thuc': ket_thuc,
        'loc_nhanh': loc_nhanh,
    }
    return render(request, 'BaoCao/bao_cao_nhap_kho.html', context)


def bao_cao_doanh_thu(request):
    # 1. Lấy tham số lọc
    loc_nhanh = request.GET.get('loc_nhanh', '')
    bat_dau = request.GET.get('bat_dau')
    ket_thuc = request.GET.get('ket_thuc')
    today = timezone.now().date()

    # Logic lọc nhanh (Đồng bộ với các báo cáo trước)
    if loc_nhanh == 'ngay':
        bat_dau = ket_thuc = today.strftime('%Y-%m-%d')
    elif loc_nhanh == 'tuan':
        bat_dau = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
        ket_thuc = today.strftime('%Y-%m-%d')
    elif loc_nhanh == 'thang':
        bat_dau = today.replace(day=1).strftime('%Y-%m-%d')
        ket_thuc = today.strftime('%Y-%m-%d')
    elif loc_nhanh == 'nam':
        bat_dau = today.replace(month=1, day=1).strftime('%Y-%m-%d')
        ket_thuc = today.strftime('%Y-%m-%d')

    # 2. Lọc các đơn hàng GIAO THÀNH CÔNG
    lich_su_thanh_cong = LichSuDonHang.objects.filter(trang_thai='thanh_cong')
    if bat_dau:
        lich_su_thanh_cong = lich_su_thanh_cong.filter(thoi_gian__date__gte=bat_dau)
    if ket_thuc:
        lich_su_thanh_cong = lich_su_thanh_cong.filter(thoi_gian__date__lte=ket_thuc)

    # Lấy danh sách ID phiếu xuất đã thành công
    danh_sach_px_id = lich_su_thanh_cong.values_list('phieu_xuat_id', flat=True)
    phi_eu_xuat_qs = PhieuXuat.objects.filter(id__in=danh_sach_px_id)

    # 3. Tính toán tổng số đơn và tổng doanh thu
    tong_don_thanh_cong = phi_eu_xuat_qs.count()

    # Doanh thu = tổng (số lượng * giá bán sản phẩm) của các phiếu thành công
    tong_doanh_thu = ChiTietPhieuXuat.objects.filter(
        phieu_xuat__in=phi_eu_xuat_qs
    ).aggregate(
        total=Sum(F('so_luong') * F('san_pham__gia_ban'))
    )['total'] or 0

    # 4. Dữ liệu cho biểu đồ và bảng (Gom nhóm theo ngày)
    # Chúng ta lấy lịch sử thành công để biết ngày hoàn thành thực tế
    data_theo_ngay = lich_su_thanh_cong.annotate(ngay=TruncDate('thoi_gian')).values('ngay').annotate(
        so_don=Count('phieu_xuat', distinct=True),
        so_luong_sp=Sum('phieu_xuat__chitietphieuxuat__so_luong'),
        doanh_thu_ngay=Sum(
            F('phieu_xuat__chitietphieuxuat__so_luong') * F('phieu_xuat__chitietphieuxuat__san_pham__gia_ban'))
    ).order_by('-ngay')

    # Chuẩn bị list cho Chart.js
    chart_labels = [d['ngay'].strftime('%d/%m') for d in reversed(list(data_theo_ngay)[:10])]
    chart_data = [float(d['doanh_thu_ngay']) for d in reversed(list(data_theo_ngay)[:10])]

    context = {
        'tong_don_thanh_cong': tong_don_thanh_cong,
        'tong_doanh_thu': tong_doanh_thu,
        'data_theo_ngay': data_theo_ngay,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'bat_dau': bat_dau,
        'ket_thuc': ket_thuc,
        'loc_nhanh': loc_nhanh,
    }
    return render(request, 'BaoCao/bao_cao_doanh_thu.html', context)