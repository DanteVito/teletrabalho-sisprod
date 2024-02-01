from django.contrib.admin.forms import (AdminAuthenticationForm,
                                        AdminPasswordChangeForm)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.urls import reverse

# Reescrever views de login e redefinição de senhas
# Por padrão, no redirecionamento, quando o usuário é faz logout,
# ele é redirecionado para página de login do painel de admin.


class MyAdminAuthenticationForm(AdminAuthenticationForm):
    def confirm_login_allowed(self, user: AbstractBaseUser) -> None:
        ...


def login_view(request):
    form = MyAdminAuthenticationForm()

    if request.method == 'POST':
        form = MyAdminAuthenticationForm(data=request.POST)
        if form.is_valid():
            cf = form.cleaned_data
            user = authenticate(request,
                                username=cf['username'],
                                password=cf['password'])
            if user is not None:
                login(request, user)
                if user.is_staff:
                    # return redirect(reverse('admin:index'))
                    return redirect(reverse('webapp:home'))
                return redirect(reverse('authentication:password_change'))

    context = {'title': 'Login', 'form': form}
    return render(request, 'admin/login.html', context)


def password_change(request):
    form = AdminPasswordChangeForm(user=request.user)

    if request.method == 'POST':
        form = AdminPasswordChangeForm(data=request.POST,
                                       user=request.user)
        if form.is_valid():
            user = form.user
            user.is_staff = True
            servidores = Group.objects.get(name='SERVIDORES')
            servidores.user_set.add(user)
            user.save()
            form.save()
            return redirect(reverse('admin:index'))

    context = {'title': 'Redefinição da Senha', 'form': form}
    return render(request, 'admin/password_change_form.html', context)


@login_required
def logout_view(request):
    logout(request)
    return redirect(reverse('authentication:login'))
