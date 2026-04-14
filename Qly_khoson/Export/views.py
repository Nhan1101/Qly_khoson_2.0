from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Prefetch, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from suppliers.models import (
    ChiTietPhieuXuat,
    DoiTuongNhan,
    NguoiDung,
    PhieuXuat,
    SanPham,
)


def format_delivery_note_code(note_id):
    return f"PX{note_id:05d}"


def parse_positive_int(value):
    raw_value = str(value or "").strip()
    if not raw_value:
        return 0

    quantity = int(raw_value)
    if quantity < 0:
        raise ValueError("Số lượng phải lớn hơn hoặc bằng 0.")
    return quantity


def parse_decimal(value):
    raw_value = str(value or "").replace(".", "").replace(",", "").strip()
    if not raw_value:
        return Decimal("0")
    return Decimal(raw_value)


def get_operator():
    return (
        NguoiDung.objects.filter(dang_hoat_dong=True).order_by("id").first()
        or NguoiDung.objects.order_by("id").first()
    )


def get_product_rows(note=None, post_data=None):
    from Export.models import ChiTietDonDatHang # Ensure imported
    
    details = {}
    if note is not None:
        details = {detail.san_pham_id: detail for detail in note.chitietphieuxuat_set.select_related("san_pham")}

    stock_items = SanPham.objects.all()
    
    order_id = post_data.get("order_id") if post_data else None
    
    if order_id:
        # Load products from order only
        order_details = ChiTietDonDatHang.objects.filter(don_dat_hang_id=order_id).select_related('san_pham')
        stock_items = stock_items.filter(id__in=[d.san_pham_id for d in order_details])
    else:
        if note is not None:
            stock_items = stock_items.filter(Q(chitietphieuxuat__phieu_xuat=note))
        else:
            # If net-new manual delivery note, don't pre-populate anything!
            stock_items = stock_items.none()
            
    stock_items = stock_items.distinct().order_by("ten_son", "id")
    rows = []
    
    # Create an easy lookup for order quantities
    order_quantities = {}
    if order_id:
        order_details = ChiTietDonDatHang.objects.filter(don_dat_hang_id=order_id)
        order_quantities = {d.san_pham_id: d.so_luong for d in order_details}

    for stock in stock_items:
        detail = details.get(stock.id)
        posted_quantity = None
        if post_data is not None:
            raw_qty = post_data.get(f"quantity_{stock.id}")
            if raw_qty is not None:
                posted_quantity = raw_qty.strip()
                
        # If new delivery note, use order quantity if available
        default_qty = detail.so_luong if detail else order_quantities.get(stock.id, 0)
        
        rows.append(
            {
                "product": stock,
                "stock": stock,
                "quantity": posted_quantity if posted_quantity is not None else default_qty,
                "unit_price": stock.gia_ban,
            }
        )
    return rows


def get_customer_order_for_delivery(order_id, order_code):
    if order_id:
        return DonDatHang.objects.filter(pk=order_id).first()
    if order_code:
        return DonDatHang.objects.filter(ma_don=order_code).first()
    return None


def update_customer_order_status(order, export_type):
    if order is None:
        return

    status_map = {
        "full": "Đã xuất",
        "partial": "Đã xuất 1 phần",
    }
    next_status = status_map.get(export_type)
    if next_status and order.trang_thai != next_status:
        order.trang_thai = next_status
        order.save(update_fields=["trang_thai"])

def build_note_context(note=None, post_data=None):
    rows = get_product_rows(note, post_data=post_data)
    related_order = None
    if note is not None:
        related_order = get_customer_order_for_delivery("", note.ma_don)

    # We'll pass products_json for dynamic adding (all items, including out of stock)
    stock_for_json = SanPham.objects.all().order_by("ten_son", "id")
    products_data = []
    for p in stock_for_json:
        products_data.append({
            "id": p.id,
            "ten": p.ten_son,
            "ma": p.ma_son,
            "dvt": p.don_vi_tinh,
            "ton": p.so_luong_ton,
            "gia": float(p.gia_ban)
        })
    import json
    
    # We will pass rows as existing_details_json so JS can render them as initial rows
    existing_details = []
    for r in rows:
        existing_details.append({
            "product_id": r["product"].id,
            "so_luong": r["quantity"]
        })
        
    return {
        "products_json": json.dumps(products_data),
        "existing_details_json": json.dumps(existing_details),
        "note": note,
        "today": timezone.localdate(),
        "next_code": format_delivery_note_code((PhieuXuat.objects.order_by("-id").values_list("id", flat=True).first() or 0) + 1),
        "form_values": {
            "recipient_name": (post_data.get("recipient_name", "").strip() if post_data is not None else (note.doi_tuong_nhan.ten_nguoi_nhan if getattr(note, "doi_tuong_nhan", None) else "")),
            "order_code": (post_data.get("order_code", "").strip() if post_data is not None else (note.ma_don if note else "")),
            "phone": (post_data.get("phone", "").strip() if post_data is not None else (getattr(note.doi_tuong_nhan, "so_dien_thoai", "") if note else "")),
            "address": (post_data.get("address", "").strip() if post_data is not None else (getattr(note.doi_tuong_nhan, "dia_chi", "") if note else "")),
            "expected_date": (post_data.get("expected_date", "").strip() if post_data is not None else (note.du_kien_giao.isoformat() if note and note.du_kien_giao else "")),
            "reason": (post_data.get("reason", "").strip() if post_data is not None else (note.ly_do_xuat if note else "")),
            "order_id": (post_data.get("order_id", "").strip() if post_data is not None else (str(related_order.id) if related_order else "")),
            "export_type": (post_data.get("export_type", "").strip() if post_data is not None else ""),
        },
    }





def save_delivery_note(request, note=None):
    operator = get_operator()
    if operator is None:
        raise ValidationError("Chưa có tài khoản người dùng để tạo phiếu xuất.")

    recipient_name = request.POST.get("recipient_name", "").strip()
    phone = request.POST.get("phone", "").strip()
    address = request.POST.get("address", "").strip()
    order_code = request.POST.get("order_code", "").strip()
    expected_date_raw = request.POST.get("expected_date", "").strip()
    reason = request.POST.get("reason", "").strip()
    order_id = request.POST.get("order_id", "").strip()
    export_type = request.POST.get("export_type", "").strip()

    if not recipient_name:
        raise ValidationError("Vui lòng nhập nguồn nhận.")

    expected_date = expected_date_raw or None
    recipient, _ = DoiTuongNhan.objects.get_or_create(
        ten_nguoi_nhan=recipient_name,
        so_dien_thoai=phone or None,
        dia_chi=address or None,
    )

    selected_items = []
    product_ids = request.POST.getlist("product_id")
    for product_id in product_ids:
        quantity = parse_positive_int(request.POST.get(f"quantity_{product_id}", "0"))
        if quantity == 0:
            continue

        product = get_object_or_404(SanPham, pk=product_id)
        selected_items.append(
            {
                "product": product,
                "quantity": quantity,
                "unit_price": product.gia_ban,
            }
        )

    if not selected_items:
        raise ValidationError("Vui lòng nhập số lượng xuất cho ít nhất một sản phẩm.")

    total_amount = sum(item["unit_price"] * item["quantity"] for item in selected_items)

    with transaction.atomic():
        if note is None:
            note = PhieuXuat.objects.create(
                doi_tuong_nhan=recipient,
                nguoi_dung=operator,
                ma_don=order_code,
                du_kien_giao=expected_date,
                ly_do_xuat=reason,
                tong_tien=total_amount,
            )
        else:
            note.doi_tuong_nhan = recipient
            note.ma_don = order_code
            note.du_kien_giao = expected_date
            note.ly_do_xuat = reason
            note.tong_tien = total_amount
            note.save(update_fields=["doi_tuong_nhan", "ma_don", "du_kien_giao", "ly_do_xuat", "tong_tien"])

        existing_details = {detail.san_pham_id: detail for detail in note.chitietphieuxuat_set.all()}
        selected_ids = set()

        for item in selected_items:
            product = item["product"]
            selected_ids.add(product.id)
            ChiTietPhieuXuat.objects.update_or_create(
                phieu_xuat=note,
                san_pham=product,
                defaults={
                    "so_luong": item["quantity"],
                    "don_gia": item["unit_price"],
                },
            )

        for product_id, detail in existing_details.items():
            if product_id not in selected_ids:
                detail.delete()

        order = get_customer_order_for_delivery(order_id, order_code)
        update_customer_order_status(order, export_type)

    return note


class DeliveryNoteListView(ListView):
    model = PhieuXuat
    template_name = "Export/delivery_note_list.html"
    context_object_name = "delivery_notes"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("doi_tuong_nhan", "nguoi_dung")
            .annotate(total_quantity=Sum("chitietphieuxuat__so_luong"))
            .order_by("-ngay_xuat", "-id")
        )

        code = self.request.GET.get("code", "").strip().upper()
        recipient = self.request.GET.get("recipient", "").strip()
        date_from = self.request.GET.get("date_from", "").strip()
        date_to = self.request.GET.get("date_to", "").strip()

        if code:
            digits = "".join(ch for ch in code if ch.isdigit())
            queryset = queryset.filter(pk=int(digits)) if digits else queryset.none()
        if recipient:
            queryset = queryset.filter(doi_tuong_nhan__ten_nguoi_nhan__icontains=recipient)
        if date_from:
            queryset = queryset.filter(ngay_xuat__gte=date_from)
        if date_to:
            queryset = queryset.filter(ngay_xuat__lte=date_to)

        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filters"] = {
            "code": self.request.GET.get("code", ""),
            "recipient": self.request.GET.get("recipient", ""),
            "date_from": self.request.GET.get("date_from", ""),
            "date_to": self.request.GET.get("date_to", ""),
        }
        return ctx


class DeliveryNoteCreateView(View):
    template_name = "Export/delivery_note_create.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, build_note_context(post_data=request.GET))

    def post(self, request, *args, **kwargs):
        try:
            note = save_delivery_note(request)
        except (ValidationError, ValueError, InvalidOperation) as exc:
            messages.error(request, str(exc))
            return render(request, self.template_name, build_note_context(post_data=request.POST))

        messages.success(request, "Đã tạo phiếu xuất kho.")
        return redirect("delivery-note-detail", pk=note.pk)


class DeliveryNoteDetailView(DetailView):
    model = PhieuXuat
    template_name = "Export/delivery_note_detail.html"
    context_object_name = "note"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("doi_tuong_nhan", "nguoi_dung")
            .prefetch_related(Prefetch("chitietphieuxuat_set", queryset=ChiTietPhieuXuat.objects.select_related("san_pham")))
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["note_details"] = [
            {
                "detail": detail,
                "line_total": detail.don_gia * detail.so_luong,
            }
            for detail in ctx["note"].chitietphieuxuat_set.all()
        ]
        return ctx


class DeliveryNoteUpdateView(View):
    template_name = "Export/delivery_note_edit.html"

    def get_object(self, pk):
        return get_object_or_404(
            PhieuXuat.objects.select_related("doi_tuong_nhan", "nguoi_dung").prefetch_related("chitietphieuxuat_set"),
            pk=pk,
        )

    def get(self, request, pk, *args, **kwargs):
        note = self.get_object(pk)
        return render(request, self.template_name, build_note_context(note))

    def post(self, request, pk, *args, **kwargs):
        note = self.get_object(pk)
        try:
            note = save_delivery_note(request, note=note)
        except (ValidationError, ValueError, InvalidOperation) as exc:
            messages.error(request, str(exc))
            return render(request, self.template_name, build_note_context(note, post_data=request.POST))

        messages.success(request, "Đã cập nhật phiếu xuất kho.")
        return redirect("delivery-note-detail", pk=note.pk)


import json


class DeliveryOrderCreateView(View):
    template_name = "Export/delivery_order_create.html"

    def get_note(self, note_id):
        return get_object_or_404(
            PhieuXuat.objects.select_related("doi_tuong_nhan").prefetch_related(
                Prefetch("chitietphieuxuat_set", queryset=ChiTietPhieuXuat.objects.select_related("san_pham"))
            ),
            pk=note_id,
        )

    def get_context_data(self, note):
        note_details = []
        for detail in note.chitietphieuxuat_set.all():
            note_details.append(
                {
                    "ten_hang": detail.san_pham.ten_son,
                    "ma_hang": detail.san_pham.ma_son,
                    "don_vi_tinh": detail.san_pham.don_vi_tinh,
                    "don_gia": detail.don_gia,
                    "so_luong": detail.so_luong,
                    "thanh_tien": detail.don_gia * detail.so_luong,
                }
            )
        return {"note": note, "note_details": note_details}

    def get(self, request, *args, **kwargs):
        note_id = request.GET.get("note_id", "").strip()
        if not note_id:
            messages.error(request, "Không tìm thấy phiếu xuất kho để tạo đơn giao hàng.")
            return redirect("delivery-note-list")

        note = self.get_note(note_id)
        return render(request, self.template_name, self.get_context_data(note))

    def post(self, request, *args, **kwargs):
        note_id = request.POST.get("note_id", "").strip()
        if not note_id:
            messages.error(request, "Không tìm thấy phiếu xuất kho để lưu đơn giao hàng.")
            return redirect("delivery-note-list")

        note = self.get_note(note_id)
        if not note.da_tao_don_giao_hang:
            note.da_tao_don_giao_hang = True
            note.save(update_fields=["da_tao_don_giao_hang"])

        messages.success(request, "Đã tạo đơn giao hàng thành công.")
        return redirect("delivery-note-list")


class ProductCatalogView(ListView):
    model = SanPham
    template_name = "Export/product_catalog.html"
    context_object_name = "products"
    paginate_by = 10
    
    def get_queryset(self):
        return super().get_queryset().order_by("-id")
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page_obj = ctx.get("page_obj")
        start_index = page_obj.start_index() if page_obj else 1
        rows = []
        for i, sp in enumerate(ctx['products'], start_index):
            ton = sp.so_luong_ton
            gia_ban = f"{sp.gia_ban:,.0f}".replace(",", ".")
            gia_nhap = f"{sp.gia_nhap:,.0f}".replace(",", ".")
            rows.append({
                "stt": i,
                "ten": sp.ten_son,
                "ma": sp.ma_son,
                "loai": sp.loai_son,
                "dvt": sp.don_vi_tinh,
                "ton": ton,
                "giaBan": gia_ban,
                "giaVon": gia_nhap
            })
        ctx['products_json'] = json.dumps(rows)
        return ctx

from Export.models import DonDatHang

class CustomerOrderListView(ListView):
    model = DonDatHang
    template_name = "Export/customer_order_list.html"
    context_object_name = "orders"
    paginate_by = 10
    
    def get_queryset(self):
        return super().get_queryset().select_related("doi_tuong_nhan").order_by("-id")
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page_obj = ctx.get("page_obj")
        start_index = page_obj.start_index() if page_obj else 1
        rows = []
        for i, order in enumerate(ctx['orders'], start_index):
            ten_kh = order.doi_tuong_nhan.ten_nguoi_nhan if order.doi_tuong_nhan else ""
            rows.append({
                "stt": i,
                "id": order.id,
                "ma": order.ma_don,
                "ten": ten_kh,
                "gia": f"{order.tong_tien:,.0f}".replace(",", ".") + " đ",
                "time": order.ngay_dat.strftime("%d/%m/%Y %H:%M"),
                "st": order.trang_thai,
            })
        ctx['orders_json'] = json.dumps(rows)
        return ctx

from datetime import timedelta
from django.utils import timezone
from suppliers.models import SanPham, ChiTietPhieuNhap

class InventoryAlertView(ListView):
    model = SanPham
    template_name = "Export/inventory_alert.html"
    context_object_name = "products"
    paginate_by = 10

    def get_queryset(self):
        from django.db.models import F
        return super().get_queryset().filter(so_luong_ton__lte=F('muc_toi_thieu')).order_by("so_luong_ton", "id")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page_obj = ctx.get("page_obj")
        start_index = page_obj.start_index() if page_obj else 1
        rows = []
        for i, sp in enumerate(ctx['products'], start_index):
            tt = "Nguy cấp" if sp.so_luong_ton == 0 else "Thiếu nhẹ"
            rows.append({
                "stt": i,
                "ten": sp.ten_son,
                "ton": sp.so_luong_ton,
                "min": sp.muc_toi_thieu,
                "tt": tt
            })
        ctx['inventory_json'] = json.dumps(rows)
        return ctx

class ExpiryAlertView(ListView):
    model = ChiTietPhieuNhap
    template_name = "Export/expiry_alert.html"
    context_object_name = "batches"
    paginate_by = 10

    def get_queryset(self):
        threshold_date = timezone.now().date() + timedelta(days=60) # 60 days alert
        return super().get_queryset().select_related('san_pham').filter(exp_date__lte=threshold_date, so_luong__gt=0).order_by("exp_date", "id")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page_obj = ctx.get("page_obj")
        start_index = page_obj.start_index() if page_obj else 1
        rows = []
        today = timezone.now().date()
        for i, batch in enumerate(ctx['batches'], start_index):
            days_left = (batch.exp_date - today).days
            if days_left < 0:
                muc = f"Đã quá hạn {-days_left} ngày"
                tt = "Hết hạn"
            else:
                muc = f"{days_left} ngày"
                tt = "Sắp hết"
            rows.append({
                "stt": i,
                "ten": batch.san_pham.ten_son,
                "han": batch.exp_date.strftime("%d/%m/%Y"),
                "muc": muc,
                "tt": tt
            })
        ctx['expiry_json'] = json.dumps(rows)
        return ctx

def save_customer_order(request, order=None):
    customer_name = request.POST.get("customer_name", "").strip()
    phone = request.POST.get("phone", "").strip()
    address = request.POST.get("address", "").strip()
    order_code = request.POST.get("order_code", "").strip()
    order_date = request.POST.get("order_date", "").strip()
    note = request.POST.get("note", "").strip()

    if not customer_name:
        raise ValidationError("Vui lòng nhập tên khách hàng.")

    if not order_code:
        # Tự động sinh mã đơn nếu không có
        next_id = (DonDatHang.objects.order_by("-id").values_list("id", flat=True).first() or 0) + 1
        order_code = f"DH{next_id:05d}"
        
    recipient, _ = DoiTuongNhan.objects.get_or_create(
        ten_nguoi_nhan=customer_name,
        so_dien_thoai=phone or None,
        dia_chi=address or None,
    )

    selected_items = []
    product_ids = request.POST.getlist("product_ids")
    quantities = request.POST.getlist("quantities")
    
    for pid, qty in zip(product_ids, quantities):
        pid = pid.strip()
        qty = parse_positive_int(qty)
        if not pid or qty == 0:
            continue
            
        product = get_object_or_404(SanPham, pk=pid)
        selected_items.append({
            "product": product,
            "quantity": qty,
            "unit_price": product.gia_ban,
        })
        
    if not selected_items:
        raise ValidationError("Vui lòng thêm ít nhất một sản phẩm hợp lệ vào đơn.")

    total_amount = sum(item["unit_price"] * item["quantity"] for item in selected_items)

    from Export.models import ChiTietDonDatHang # Tối ưu hóa import

    with transaction.atomic():
        if order is None:
            order = DonDatHang.objects.create(
                ma_don=order_code,
                doi_tuong_nhan=recipient,
                tong_tien=total_amount,
                ghi_chu=note,
            )
            # Không cập nhật ngay_dat nếu chưa set explicitly thông qua models? DB auto_now_add.
        else:
            order.doi_tuong_nhan = recipient
            if order_code:
                order.ma_don = order_code
            order.ghi_chu = note
            order.tong_tien = total_amount
            order.save(update_fields=["doi_tuong_nhan", "ma_don", "ghi_chu", "tong_tien"])
            
        existing_details = {detail.san_pham_id: detail for detail in order.details.all()}
        selected_ids = set()

        for item in selected_items:
            product = item["product"]
            selected_ids.add(product.id)
            ChiTietDonDatHang.objects.update_or_create(
                don_dat_hang=order,
                san_pham=product,
                defaults={
                    "so_luong": item["quantity"],
                    "don_gia": item["unit_price"],
                    "thanh_tien": item["quantity"] * item["unit_price"]
                },
            )

        for product_id, detail in existing_details.items():
            if product_id not in selected_ids:
                detail.delete()

    return order

class CustomerOrderCreateView(View):
    template_name = "Export/customer_order_create.html"

    def get_context_data(self, **kwargs):
        ctx = {}
        products = SanPham.objects.all().order_by("ten_son", "id")
        products_data = []
        for p in products:
            products_data.append({
                "id": p.id,
                "ten": p.ten_son,
                "ma": p.ma_son,
                "dvt": p.don_vi_tinh,
                "gia": float(p.gia_ban)
            })
        ctx['products_json'] = json.dumps(products_data)
        if 'error' in kwargs:
            ctx['error'] = kwargs['error']
        return ctx

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())
        
    def post(self, request, *args, **kwargs):
        try:
            order = save_customer_order(request)
            messages.success(request, "Đã tạo đơn đặt hàng.")
            return redirect("customer-order-detail", pk=order.pk)
        except (ValidationError, ValueError, InvalidOperation) as exc:
            return render(request, self.template_name, self.get_context_data(error=str(exc)))

class CustomerOrderUpdateView(View):
    template_name = "Export/customer_order_edit.html"

    def get_object(self, pk):
        return get_object_or_404(
            DonDatHang.objects.select_related("doi_tuong_nhan").prefetch_related("details__san_pham"),
            pk=pk,
        )

    def get_context_data(self, order, **kwargs):
        ctx = {"order": order}
        products = SanPham.objects.all().order_by("ten_son", "id")
        products_data = []
        for p in products:
            products_data.append({
                "id": p.id,
                "ten": p.ten_son,
                "ma": p.ma_son,
                "dvt": p.don_vi_tinh,
                "gia": float(p.gia_ban)
            })
        ctx['products_json'] = json.dumps(products_data)
        
        details_data = []
        for d in order.details.select_related('san_pham').all():
            details_data.append({
                "product_id": d.san_pham_id,
                "so_luong": d.so_luong,
            })
        ctx['existing_details_json'] = json.dumps(details_data)
        if 'error' in kwargs:
            ctx['error'] = kwargs['error']
        return ctx

    def get(self, request, pk, *args, **kwargs):
        order = self.get_object(pk)
        return render(request, self.template_name, self.get_context_data(order))
        
    def post(self, request, pk, *args, **kwargs):
        order = self.get_object(pk)
        try:
            order = save_customer_order(request, order=order)
            messages.success(request, "Đã cập nhật đơn đặt hàng.")
            return redirect("customer-order-detail", pk=order.pk)
        except (ValidationError, ValueError, InvalidOperation) as exc:
            return render(request, self.template_name, self.get_context_data(order, error=str(exc)))

class CustomerOrderDetailView(DetailView):
    model = DonDatHang
    template_name = "Export/customer_order_detail.html"
    context_object_name = "order"

class CustomerOrderDeleteView(View):
    def post(self, request, pk, *args, **kwargs):
        order = get_object_or_404(DonDatHang, pk=pk)
        order.delete()
        messages.success(request, "Đã xóa đơn đặt hàng thành công.")
        return JsonResponse({"success": True})
