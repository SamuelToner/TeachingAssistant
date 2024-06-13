# auth_app/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class EditProfileForm(UserChangeForm):
    password = None  # This is to remove the password field from the form

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]


class CalculatorForm(forms.Form):
    OPERATOR_CHOICES = [
        ("+", "Add"),
        ("-", "Subtract"),
        ("*", "Multiply"),
        ("/", "Divide"),
    ]

    operand1 = forms.DecimalField()
    operator = forms.ChoiceField(choices=OPERATOR_CHOICES)
    operand2 = forms.DecimalField()
