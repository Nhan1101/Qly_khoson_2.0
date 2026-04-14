from django.urls import path
from . import views

app_name = 'tongquat'

urlpatterns = [
    # Đây là đường dẫn khi vào app Tongquat
    path('', views.index, name='index'),
]