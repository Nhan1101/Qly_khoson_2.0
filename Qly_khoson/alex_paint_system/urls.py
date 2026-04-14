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
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(TemplateView.as_view(template_name='base.html'), login_url='dang-nhap:login'), name='home'),
    path('dang-nhap/', include('DangNhap.urls')),
    path('suppliers/', include('suppliers.urls')),
    path('quan-ly-tai-khoa/', include('QuanLyTaiKhoa.urls')),
    path('quan-ly-kiem-ke/', include('QuanLyKiemKe.urls')),
    path('', include('nhapkho.urls')),
    path('admin/', admin.site.urls),
]
