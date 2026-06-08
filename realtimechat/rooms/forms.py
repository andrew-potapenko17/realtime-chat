from django import forms

from .models import Room


class CreateRoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ("name", "description", "room_type", "is_private")
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "e.g. general, design, backend",
                "autofocus": True,
            }),
            "description": forms.TextInput(attrs={
                "placeholder": "What's this room about? (optional)",
            }),
            "room_type": forms.Select(),
            "is_private": forms.CheckboxInput(),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if Room.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("A room with this name already exists.")
        return name


class EditRoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ("description", "is_private")
        widgets = {
            "description": forms.TextInput(attrs={
                "placeholder": "What's this room about? (optional)",
            }),
            "is_private": forms.CheckboxInput(),
        }