from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.views import View

from .forms import LoginForm


class LoginView(View):
    template_name = 'dangnhap/login.html'
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            return redirect('home')
        return render(request, self.template_name, {'form': form}, status=400)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('dang-nhap:login')

