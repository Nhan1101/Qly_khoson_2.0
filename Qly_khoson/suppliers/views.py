from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from .models import NhaCungCap


class SupplierListView(ListView):
    model = NhaCungCap
    template_name = "suppliers/index.html"
    context_object_name = "suppliers"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by("id")
        ma_ncc = self.request.GET.get("ma_ncc", "").strip().upper()
        ten_ncc = self.request.GET.get("ten_ncc", "").strip()
        email = self.request.GET.get("email", "").strip()
        so_dien_thoai = self.request.GET.get("so_dien_thoai", "").strip()
        dia_chi = self.request.GET.get("dia_chi", "").strip()

        if ma_ncc:
            normalized = ma_ncc.replace("NCC_", "").replace("NCC", "").strip()
            if normalized.isdigit():
                queryset = queryset.filter(pk=int(normalized))
            else:
                queryset = queryset.none()

        if ten_ncc:
            queryset = queryset.filter(ten_ncc__icontains=ten_ncc)
        if email:
            queryset = queryset.filter(email__icontains=email)
        if so_dien_thoai:
            queryset = queryset.filter(so_dien_thoai__icontains=so_dien_thoai)
        if dia_chi:
            queryset = queryset.filter(dia_chi__icontains=dia_chi)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filters"] = {
            "ma_ncc": self.request.GET.get("ma_ncc", ""),
            "ten_ncc": self.request.GET.get("ten_ncc", ""),
            "email": self.request.GET.get("email", ""),
            "so_dien_thoai": self.request.GET.get("so_dien_thoai", ""),
            "dia_chi": self.request.GET.get("dia_chi", ""),
        }
        return context


def _validate_supplier_payload(request):
    ten_ncc = request.POST.get("ten_ncc", "").strip()
    so_dien_thoai = request.POST.get("so_dien_thoai", "").strip()
    email = request.POST.get("email", "").strip() or None
    dia_chi = request.POST.get("dia_chi", "").strip() or None

    if not ten_ncc:
        return None, JsonResponse({"success": False, "error": "Ten nha cung cap la bat buoc."}, status=400)
    if not so_dien_thoai:
        return None, JsonResponse({"success": False, "error": "So dien thoai la bat buoc."}, status=400)

    payload = {
        "ten_ncc": ten_ncc,
        "so_dien_thoai": so_dien_thoai,
        "email": email,
        "dia_chi": dia_chi,
    }
    return payload, None


@require_POST
def supplier_create(request):
    payload, error_response = _validate_supplier_payload(request)
    if error_response:
        return error_response

    if NhaCungCap.objects.filter(ten_ncc__iexact=payload["ten_ncc"]).exists():
        return JsonResponse(
            {"success": False, "error": "Ten nha cung cap da ton tai."},
            status=400,
        )

    supplier = NhaCungCap.objects.create(**payload)
    return JsonResponse(
        {
            "success": True,
            "id": supplier.pk,
            "ma_ncc": supplier.ma_ncc,
        }
    )


@require_POST
def supplier_update(request, pk):
    payload, error_response = _validate_supplier_payload(request)
    if error_response:
        return error_response

    supplier = NhaCungCap.objects.filter(pk=pk).first()
    if supplier is None:
        return JsonResponse({"success": False, "error": "Khong tim thay nha cung cap."}, status=404)

    duplicate_exists = NhaCungCap.objects.filter(
        Q(ten_ncc__iexact=payload["ten_ncc"]) & ~Q(pk=supplier.pk)
    ).exists()
    if duplicate_exists:
        return JsonResponse(
            {"success": False, "error": "Ten nha cung cap da ton tai."},
            status=400,
        )

    for field, value in payload.items():
        setattr(supplier, field, value)
    supplier.save()
    return JsonResponse({"success": True})


@require_POST
def supplier_delete(request, pk):
    supplier = NhaCungCap.objects.filter(pk=pk).first()
    if supplier is None:
        return JsonResponse({"success": False, "error": "Khong tim thay nha cung cap."}, status=404)

    supplier.delete()
    return JsonResponse({"success": True})

