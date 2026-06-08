from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EditProfileForm
from .models import UserProfile

User = get_user_model()


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile, _ = UserProfile.objects.get_or_create(user=user)

    return render(request, "profiles/profile.html", {
        "profile_user": user,
        "profile": profile,
        "is_own_profile": request.user == user,
    })


@login_required
def edit_profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = EditProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=profile,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("profiles:profile", username=request.user.username)

    return render(request, "profiles/edit_profile.html", {
        "form": form,
        "profile": profile,
    })


@login_required
def remove_avatar_view(request):
    if request.method == "POST":
        profile = get_object_or_404(UserProfile, user=request.user)
        if profile.avatar:
            profile.avatar.delete(save=False)
            profile.avatar = None
            profile.save(update_fields=["avatar"])
        messages.success(request, "Avatar removed.")
        return redirect("profiles:edit")
    return redirect("profiles:edit")