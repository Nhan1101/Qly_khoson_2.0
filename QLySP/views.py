from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import F
from django.utils import timezone
from datetime import timedelta

# Import các Model cần thiết
from suppliers.models import SanPham, TonKho, ChiTietPhieuNhap
from .forms import SanPhamForm


# ================= 1. DANH MỤC SẢN PHẨM (XỬ LÝ CẢ HIỂN THỊ, TÌM KIẾM VÀ TẠO MỚI) =================
def danh_muc_sp(request):
    # Xử lý khi nhấn nút "Lưu sản phẩm" (POST)
    if request.method == 'POST':
        form = SanPhamForm(request.POST)
        if form.is_valid():
            # Lưu sản phẩm (Model tự tính giá bán và sinh mã)
            san_pham = form.save()

            # Tạo hoặc cập nhật mức tồn kho tối thiểu cho sản phẩm này
            muc_min = form.cleaned_data.get('muc_toi_thieu', 0)
            TonKho.objects.update_or_create(
                san_pham=san_pham,
                defaults={'muc_toi_thieu': muc_min}
            )
            return redirect('danh_muc_sp')
        else:
            print("LỖI FORM:", form.errors)
    else:
        form = SanPhamForm()

    # Logic lấy danh sách và tìm kiếm (GET)
    products = SanPham.objects.all().order_by('-ngay_tao')

    ma_hang = request.GET.get('ma_hang', '')
    ten_hang = request.GET.get('ten_hang', '')

    if ma_hang:
        products = products.filter(ma_son__icontains=ma_hang)
    if ten_hang:
        products = products.filter(ten_son__icontains=ten_hang)

    return render(request, 'danhmuc.html', {
        'products': products,
        'form': form,
        'ma_hang': ma_hang,
        'ten_hang': ten_hang
    })


# ================= 2. CHỈNH SỬA SẢN PHẨM (XỬ LÝ QUA AJAX) =================
def sua_san_pham(request, pk):
    san_pham = get_object_or_404(SanPham, pk=pk)
    if request.method == 'POST':
        form = SanPhamForm(request.POST, instance=san_pham)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ'})


# ================= 3. XÓA SẢN PHẨM =================
def xoa_san_pham(request, pk):
    san_pham = get_object_or_404(SanPham, pk=pk)
    san_pham.delete()
    return redirect('danh_muc_sp')


# ================= 4. CẢNH BÁO TỒN KHO =================
def canh_bao_ton_kho(request):
    # Lấy các sản phẩm có số lượng tồn <= mức tối thiểu
    danh_sach_canh_bao = TonKho.objects.filter(
        so_luong_ton__lte=F('muc_toi_thieu')
    ).select_related('san_pham')

    return render(request, 'canhbao.html', {
        'danh_sach_canh_bao': danh_sach_canh_bao
    })


# ================= 5. CẢNH BÁO HẠN SỬ DỤNG =================
def canh_bao_han_su_dung(request):
    ngay_hien_tai = timezone.now().date()
    # Mốc cảnh báo 15 ngày
    moc_canh_bao = ngay_hien_tai + timedelta(days=15)

    # Truy vấn từ ChiTietPhieuNhap (nơi chứa ma_lo và han_su_dung)
    lo_sap_het_han = ChiTietPhieuNhap.objects.filter(
        han_su_dung__lte=moc_canh_bao,
        han_su_dung__gte=ngay_hien_tai
    ).select_related('san_pham').order_by('han_su_dung')

    for lo in lo_sap_het_han:
        # Tính số ngày còn lại để hiển thị ở giao diện
        lo.so_ngay_con_lai = (lo.han_su_dung - ngay_hien_tai).days

    # LƯU Ý: Phải có tiền tố QLySP/ nếu bạn để file trong thư mục templates/QLySP/
    return render(request, 'canh_bao_hsd.html', {
        'lo_sap_het_han': lo_sap_het_han,
        'ngay_hien_tai': ngay_hien_tai
    })