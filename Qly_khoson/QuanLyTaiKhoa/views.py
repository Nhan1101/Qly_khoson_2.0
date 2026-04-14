from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from .forms import AccountForm
from suppliers.models import NguoiDung


class AccountListView(ListView):
    model = NguoiDung
    template_name = "taikhoan/index.html"
    context_object_name = "accounts"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().order_by("-ngay_tao", "-id")
        full_name = self.request.GET.get("full_name", "").strip()
        username = self.request.GET.get("username", "").strip()
        role = self.request.GET.get("role", "").strip()

        if full_name:
            queryset = queryset.filter(
                Q(first_name__icontains=full_name) | Q(last_name__icontains=full_name)
            )

        if username:
            queryset = queryset.filter(username__icontains=username)

        if role:
            queryset = queryset.filter(vai_tro=role)

        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filters"] = {
            "full_name": self.request.GET.get("full_name", ""),
            "username": self.request.GET.get("username", ""),
            "role": self.request.GET.get("role", ""),
        }
        params = self.request.GET.copy()
        params.pop("page", None)
        query_string = params.urlencode()
        ctx["query_suffix"] = f"&{query_string}" if query_string else ""
        edit_url = reverse("taikhoan_edit", args=[0])
        ctx["edit_url_template"] = edit_url.replace("/0/", "/{id}/", 1)
        return ctx


class AccountCreateView(View):
    def post(self, request, *args, **kwargs):
        form = AccountForm(request.POST, require_password=True)
        next_url = request.POST.get("next") or reverse("taikhoan_list")
        if form.is_valid():
            form.save()
            messages.success(request, "Đã tạo tài khoản.")
        else:
            messages.error(request, "Không thể tạo tài khoản, kiểm tra dữ liệu.")
        return redirect(next_url)


class AccountUpdateView(View):
    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(NguoiDung, pk=pk)
        form = AccountForm(request.POST, instance=user)
        next_url = request.POST.get("next") or reverse("taikhoan_list")
        if form.is_valid():
            form.save()
            messages.success(request, "Đã cập nhật tài khoản.")
        else:
            messages.error(request, "Không thể cập nhật tài khoản, kiểm tra dữ liệu.")
        return redirect(next_url)


class AccountDeleteView(View):
    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(NguoiDung, pk=pk)
        next_url = request.POST.get("next") or reverse("taikhoan_list")
        user.delete()
        messages.success(request, "Đã xóa tài khoản.")
        return redirect(next_url)
