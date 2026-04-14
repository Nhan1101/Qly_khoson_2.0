from django import forms

from suppliers.models import SanPham


class SanPhamForm(forms.ModelForm):
    LOAI_SON_CHOICES = [
        ("", "--- Chọn loại sơn ---"),
        ("Sơn ngoại thất", "Sơn ngoại thất"),
        ("Sơn nội thất", "Sơn nội thất"),
        ("Sơn chống thấm", "Sơn chống thấm"),
        ("Sơn chuyên dụng", "Sơn chuyên dụng"),
        ("Bột bả mastic", "Bột bả mastic"),
    ]

    loai_son = forms.ChoiceField(
        choices=LOAI_SON_CHOICES,
        label="Loại sơn",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = SanPham
        fields = ["ma_son", "ten_son", "loai_son", "don_vi_tinh", "gia_nhap", "gia_ban", "muc_toi_thieu"]
