from django import forms

from .models import UserProfile


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("avatar", "bio")
        widgets = {
            "bio": forms.TextInput(attrs={
                "placeholder": "Tell people a little about yourself…",
                "maxlength": 160,
            }),
            "avatar": forms.FileInput(),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar and hasattr(avatar, "size"):
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Avatar must be under 2 MB.")
            valid_types = ("image/jpeg", "image/png", "image/webp", "image/gif")
            if hasattr(avatar, "content_type") and avatar.content_type not in valid_types:
                raise forms.ValidationError("Only JPEG, PNG, WebP or GIF avatars are allowed.")
        return avatar