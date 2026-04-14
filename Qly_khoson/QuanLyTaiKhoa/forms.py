from django import forms

from suppliers.models import NguoiDung


class AccountForm(forms.ModelForm):
    full_name = forms.CharField(
        label="Họ tên",
        max_length=255,
        widget=forms.TextInput(attrs={"autocomplete": "name"}),
    )
    password = forms.CharField(
        label="Mật khẩu",
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = NguoiDung
        fields = ("username", "vai_tro")

    def __init__(self, *args, require_password=False, **kwargs):
        self.require_password = require_password
        super().__init__(*args, **kwargs)
        if self.require_password:
            self.fields["password"].required = True

    def clean_full_name(self):
        raw = self.cleaned_data.get("full_name", "").strip()
        if not raw and not self.instance.pk:
            raise forms.ValidationError("Họ tên là trường bắt buộc.")
        return raw

    def clean_password(self):
        password = self.cleaned_data.get("password", "")
        if self.require_password and not password:
            raise forms.ValidationError("Mật khẩu là trường bắt buộc.")
        return password

    def save(self, commit=True):
        instance = super().save(commit=False)
        full_name = self.cleaned_data.get("full_name", "").strip()
        if full_name:
            instance.first_name = full_name
        password = self.cleaned_data.get("password")
        if password:
            instance.set_password(password)
        if commit:
            instance.save()
        return instance
