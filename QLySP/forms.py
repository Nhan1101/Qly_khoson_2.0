from django import forms  # <-- THÊM DÒNG NÀY VÀO ĐẦU FILE
from suppliers.models import SanPham, TonKho


class SanPhamForm(forms.ModelForm):
    # Thêm danh sách lựa chọn cho loại sơn
    LOAI_SON_CHOICES = [
        ('', '--- Chọn loại sơn ---'),
        ('Sơn ngoại thất', 'Sơn ngoại thất'),
        ('Sơn nội thất', 'Sơn nội thất'),
        ('Sơn chống thấm', 'Sơn chống thấm'),
        ('Sơn chuyên dụng', 'Sơn chuyên dụng'),
        ('Bột bả mastic', 'Bột bả mastic'),
    ]

    # Ghi đè loai_son để hiển thị dạng danh sách chọn
    loai_son = forms.ChoiceField(
        choices=LOAI_SON_CHOICES,
        label='Loại sơn',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Thêm field này để khớp với logic Model của bạn
    muc_toi_thieu = forms.IntegerField(label='Mức tối thiểu', initial=0)

    class Meta:
        model = SanPham
        fields = ['ma_son', 'ten_son', 'loai_son', 'don_vi_tinh', 'gia_nhap','ty_le_loi_nhuan']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # QUAN TRỌNG: Cho phép mã hàng trống để vượt qua bước is_valid()
        self.fields['ma_son'].required = False
        self.fields['ma_son'].widget.attrs['placeholder'] = 'Mã sẽ tự sinh...'