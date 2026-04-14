from django.urls import path

from .views import (
    DeliveryNoteCreateView,
    DeliveryNoteDetailView,
    DeliveryNoteListView,
    DeliveryNoteUpdateView,
)


urlpatterns = [
    path("", DeliveryNoteListView.as_view(), name="delivery-note-list"),
    path("tao-moi/", DeliveryNoteCreateView.as_view(), name="delivery-note-create"),
    path("<int:pk>/", DeliveryNoteDetailView.as_view(), name="delivery-note-detail"),
    path("<int:pk>/sua/", DeliveryNoteUpdateView.as_view(), name="delivery-note-edit"),
]
