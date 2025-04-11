from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import Equipment

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'brand', 'serial_number', 'available', 'condition']



class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, label="Select Role")

    class Meta:
        model = CustomUser
        fields = ["username","email",'password1','password2','role']


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())