from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ChangePasswordForm, LoginForm, RegisterForm

User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect("rooms:lobby")

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome, {user.username}!")
        return redirect("rooms:lobby")

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("rooms:lobby")

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        next_url = request.GET.get("next")
        if next_url and next_url.startswith("/"):
            return redirect(next_url)
        return redirect("rooms:lobby")

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("accounts:login")
    return redirect("rooms:lobby")


@login_required
def change_password_view(request):
    form = ChangePasswordForm(user=request.user, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Password changed successfully.")
        return redirect("accounts:change-password")

    return render(request, "accounts/change_password.html", {"form": form})


@login_required
def delete_account_view(request):
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.info(request, "Your account has been deleted.")
        return redirect("accounts:login")

    return render(request, "accounts/delete_account.html")