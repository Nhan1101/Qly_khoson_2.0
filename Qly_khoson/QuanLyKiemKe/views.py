from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView

from suppliers.models import ChiTietPhieuKiemKe, NguoiDung, PhieuKiemKe, SanPham


def apply_ticket_display_state(ticket):
    ticket.display_code = f"KK{ticket.pk:05d}"
    details = list(ticket.chitietphieukiemke_set.all())
    has_difference = any(detail.chenh_lech != 0 for detail in details)
    if ticket.trang_thai == "draft" and not details:
        ticket.display_status = "Đang làm"
        ticket.display_status_class = "status-draft"
    elif has_difference:
        ticket.display_status = "Chênh lệch"
        ticket.display_status_class = "status-diff"
    else:
        ticket.display_status = "Khớp"
        ticket.display_status_class = "status-match"


def build_ticket_detail_rows(ticket, data=None):
    stock_items = list(
        SanPham.objects.all().order_by("ten_son", "id")
    )
    existing_details = {
        detail.san_pham_id: detail
        for detail in ticket.chitietphieukiemke_set.select_related("san_pham")
    }

    rows = []
    errors = []

    for index, sp in enumerate(stock_items, start=1):
        detail = existing_details.get(sp.id)
        actual_key = f"actual_{sp.id}"
        reason_key = f"reason_{sp.id}"

        if data is None:
            actual_raw = "" if detail is None else str(detail.so_luong_thuc_te)
            reason_raw = "" if detail is None or not detail.ly_do else detail.ly_do
        else:
            actual_raw = data.get(actual_key, "").strip()
            reason_raw = data.get(reason_key, "").strip()

        difference = ""
        actual_error = ""
        reason_error = ""

        if actual_raw:
            try:
                actual_value = int(actual_raw)
                if actual_value < 0:
                    actual_error = "Tồn thực tế phải lớn hơn hoặc bằng 0."
                else:
                    difference = actual_value - sp.so_luong_ton
                    if actual_value < sp.so_luong_ton and not reason_raw:
                        reason_error = "Vui lòng nhập lý do khi tồn thực tế nhỏ hơn hệ thống."
            except ValueError:
                actual_error = "Tồn thực tế phải là số nguyên."

        if actual_error or reason_error:
            errors.append(sp.id)

        rows.append(
            {
                "index": index,
                "stock": sp,
                "actual_name": actual_key,
                "reason_name": reason_key,
                "actual_raw": actual_raw,
                "reason_raw": reason_raw,
                "difference": difference,
                "actual_error": actual_error,
                "reason_error": reason_error,
            }
        )

    return rows, errors


class KiemKeListView(ListView):
    model = PhieuKiemKe
    template_name = "kiemke/index.html"
    context_object_name = "tickets"
    paginate_by = 12

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("nguoi_dung")
            .prefetch_related("chitietphieukiemke_set")
            .order_by("-ngay_tao", "-id")
        )
        ma_phieu = self.request.GET.get("ma_phieu", "").strip().upper()
        ngay_tao = self.request.GET.get("ngay_tao", "").strip()
        nguoi_thuc_hien = self.request.GET.get("nguoi_thuc_hien", "").strip()

        if ma_phieu:
            normalized_code = ma_phieu.replace("KK", "", 1) if ma_phieu.startswith("KK") else ma_phieu
            digits = "".join(ch for ch in normalized_code if ch.isdigit())
            queryset = queryset.filter(pk=int(digits)) if digits else queryset.none()

        if ngay_tao:
            queryset = queryset.filter(ngay_tao__date=ngay_tao)

        if nguoi_thuc_hien:
            queryset = queryset.filter(
                Q(nguoi_dung__username__icontains=nguoi_thuc_hien)
                | Q(nguoi_dung__first_name__icontains=nguoi_thuc_hien)
                | Q(nguoi_dung__last_name__icontains=nguoi_thuc_hien)
            )

        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page_obj = ctx.get("page_obj")
        start_index = page_obj.start_index() if page_obj else 1
        for offset, ticket in enumerate(ctx["object_list"], start=start_index):
            ticket.display_index = offset
            apply_ticket_display_state(ticket)

        ctx["filters"] = {
            "ma_phieu": self.request.GET.get("ma_phieu", ""),
            "ngay_tao": self.request.GET.get("ngay_tao", ""),
            "nguoi_thuc_hien": self.request.GET.get("nguoi_thuc_hien", ""),
        }
        ctx["updated_at"] = timezone.now()
        ctx["performers"] = NguoiDung.objects.filter(dang_hoat_dong=True).order_by(
            "first_name", "last_name", "username"
        )
        next_ticket_id = (PhieuKiemKe.objects.order_by("-id").values_list("id", flat=True).first() or 0) + 1
        ctx["next_ticket_code"] = f"KK{next_ticket_id:05d}"
        params = self.request.GET.copy()
        params.pop("page", None)
        query_string = params.urlencode()
        ctx["query_suffix"] = f"&{query_string}" if query_string else ""
        return ctx


class KiemKeCreateView(View):
    def post(self, request, *args, **kwargs):
        performer_id = request.POST.get("nguoi_dung_id")
        next_url = request.POST.get("next") or reverse("kiemke_list")

        if not performer_id:
            messages.error(request, "Vui lòng chọn người thực hiện.")
            return redirect(next_url)

        performer = get_object_or_404(NguoiDung, pk=performer_id, dang_hoat_dong=True)
        PhieuKiemKe.objects.create(nguoi_dung=performer, trang_thai="draft")
        messages.success(request, "Đã tạo phiếu kiểm kê mới.")
        return redirect(next_url)


class KiemKeDetailView(View):
    template_name = "kiemke/detail.html"

    def get_ticket(self, pk):
        return get_object_or_404(
            PhieuKiemKe.objects.select_related("nguoi_dung").prefetch_related("chitietphieukiemke_set"),
            pk=pk,
        )

    def build_context(self, ticket, rows):
        apply_ticket_display_state(ticket)
        return {
            "ticket": ticket,
            "rows": rows,
            "is_readonly": ticket.trang_thai == "completed",
        }

    def get(self, request, pk, *args, **kwargs):
        ticket = self.get_ticket(pk)
        rows, _ = build_ticket_detail_rows(ticket)
        return render(request, self.template_name, self.build_context(ticket, rows))

    def post(self, request, pk, *args, **kwargs):
        ticket = self.get_ticket(pk)
        if ticket.trang_thai == "completed":
            messages.error(request, "Phiếu đã hoàn thành, không thể chỉnh sửa.")
            return redirect("kiemke_detail", pk=ticket.pk)

        rows, errors = build_ticket_detail_rows(ticket, request.POST)
        if errors:
            context = self.build_context(ticket, rows)
            context["form_error"] = "Vui lòng kiểm tra lại các dòng dữ liệu chưa hợp lệ."
            return render(request, self.template_name, context, status=400)

        existing_details = {
            detail.san_pham_id: detail for detail in ticket.chitietphieukiemke_set.all()
        }
        with transaction.atomic():
            for row in rows:
                stock = row["stock"]
                actual_raw = row["actual_raw"]
                reason_raw = row["reason_raw"] or None
                detail = existing_details.get(stock.id)

                if not actual_raw:
                    if detail is not None:
                        detail.delete()
                    continue

                actual_value = int(actual_raw)
                ChiTietPhieuKiemKe.objects.update_or_create(
                    phieu_kiem_ke=ticket,
                    san_pham=stock,
                    defaults={
                        "so_luong_he_thong": stock.so_luong_ton,
                        "so_luong_thuc_te": actual_value,
                        "chenh_lech": actual_value - stock.so_luong_ton,
                        "ly_do": reason_raw,
                    },
                )

        if request.POST.get("action") == "complete":
            try:
                ticket.cap_nhat_ton_kho()
                messages.success(request, "Đã hoàn thành phiếu kiểm kê và cập nhật tồn kho.")
            except Exception as e:
                messages.error(request, f"Lỗi khi hoàn thành phiếu: {str(e)}")
        else:
            messages.success(request, "Đã lưu chi tiết phiếu kiểm kê.")
            
        return redirect("kiemke_detail", pk=ticket.pk)
