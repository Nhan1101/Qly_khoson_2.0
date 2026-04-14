from django import forms
from django.contrib.auth import authenticate


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Tên đăng nhập',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nhập tên đăng nhập',
            'class': 'login-input'
        })
    )
    password = forms.CharField(
        label='Mật khẩu',
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Nhập mật khẩu',
            'class': 'login-input'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            self.user = authenticate(username=username, password=password)
            if self.user is None:
                raise forms.ValidationError('Tên đăng nhập hoặc mật khẩu không đúng.')
        return cleaned_data

