"""
URL configuration for alex_paint_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from Export.views import ProductCatalogView, CustomerOrderListView, InventoryAlertView, ExpiryAlertView, CustomerOrderCreateView, CustomerOrderDetailView, CustomerOrderUpdateView, CustomerOrderDeleteView, DeliveryOrderCreateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='base.html'), name='home'),
    path('suppliers/', include('suppliers.urls')),
    path('quan-ly-tai-khoa/', include('QuanLyTaiKhoa.urls')),
    path('quan-ly-kiem-ke/', include('QuanLyKiemKe.urls')),
    path('phieu-xuat-kho/', include('Export.urls')),
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='base.html'), name='home'),

    path('don-giao-hang/tao-moi/',
         DeliveryOrderCreateView.as_view(),
         name='delivery-order-create'),

    path('don-dat-hang-khach-hang/',
         CustomerOrderListView.as_view(),
         name='customer-order-list'),

    path('don-dat-hang-khach-hang/tao-moi/',
         CustomerOrderCreateView.as_view(),
         name='customer-order-create'),

    path('don-dat-hang-khach-hang/<int:pk>/',
         CustomerOrderDetailView.as_view(),
         name='customer-order-detail'),

    path('don-dat-hang-khach-hang/<int:pk>/sua/',
         CustomerOrderUpdateView.as_view(),
         name='customer-order-edit'),

    path('don-dat-hang-khach-hang/<int:pk>/xoa/',
         CustomerOrderDeleteView.as_view(),
         name='customer-order-delete'),

    path('danh-muc-san-pham/',
         ProductCatalogView.as_view(),
         name='product-catalog'),

    path('canh-bao-ton-kho/',
         InventoryAlertView.as_view(),
         name='inventory-alert'),

    path('canh-bao-han-su-dung/',
         ExpiryAlertView.as_view(),
         name='expiry-alert'),
]
