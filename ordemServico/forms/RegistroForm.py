from django import forms
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.models import User
from ordemServico.models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ProfileRegisterForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['role', 'cpf', 'profile_picture']
