from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import *

from django import forms
from django.core.exceptions import ValidationError

class registrationform(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise  ValidationError("Username already exists")
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email)
        if r.count():
            raise  ValidationError("Email already exists")
        return email


choices=(("Business", "Business"),
        ("Personal", "Personal"),
        ("Kids", "Kids"),
        ("Private", "Private"),
        ("Other", "Other"))

class AccountForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), error_messages={'incomplete': 'Enter a phone number.'},
                validators=[RegexValidator(r'^[0-9]+$', 'Enter a valid phone number.')])
    type_of_account = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices = choices)

    class Meta:
        model = Account
        fields = ('username', 'email', 'phone_number', 'type_of_account')