from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path
from django.views.generic import TemplateView

from Export.views import (
    CustomerOrderCreateView,
    CustomerOrderDeleteView,
    CustomerOrderDetailView,
    CustomerOrderListView,
    CustomerOrderUpdateView,
    DeliveryOrderCreateView,
    ExpiryAlertView,
    InventoryAlertView,
    ProductCatalogView,
)

urlpatterns = [
    path("", login_required(TemplateView.as_view(template_name="base.html")), name="home"),
    path("dang-nhap/", include("DangNhap.urls")),
    path("suppliers/", include("suppliers.urls")),
    path("quan-ly-tai-khoa/", include("QuanLyTaiKhoa.urls")),
    path("quan-ly-kiem-ke/", include("QuanLyKiemKe.urls")),
    path("", include("nhapkho.urls")),
    path("tong-quat/", include("Tongquat.urls")),
    path("san-pham/", include("QLySP.urls")),
    path("bao-cao/", include("BaoCao.urls")),
    path("phieu-xuat-kho/", include("Export.urls")),
    path("admin/", admin.site.urls),
    path("don-giao-hang/tao-moi/", DeliveryOrderCreateView.as_view(), name="delivery-order-create"),
    path("don-dat-hang-khach-hang/", CustomerOrderListView.as_view(), name="customer-order-list"),
    path("don-dat-hang-khach-hang/tao-moi/", CustomerOrderCreateView.as_view(), name="customer-order-create"),
    path("don-dat-hang-khach-hang/<int:pk>/", CustomerOrderDetailView.as_view(), name="customer-order-detail"),
    path("don-dat-hang-khach-hang/<int:pk>/sua/", CustomerOrderUpdateView.as_view(), name="customer-order-edit"),
    path("don-dat-hang-khach-hang/<int:pk>/xoa/", CustomerOrderDeleteView.as_view(), name="customer-order-delete"),
    path("danh-muc-san-pham/", ProductCatalogView.as_view(), name="product-catalog"),
    path("canh-bao-ton-kho/", InventoryAlertView.as_view(), name="inventory-alert"),
    path("canh-bao-han-su-dung/", ExpiryAlertView.as_view(), name="expiry-alert"),
]
