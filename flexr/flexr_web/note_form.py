from django.contrib.auth.models import User
from .models import *
from datetime import date
from django.core.validators import EMPTY_VALUES
from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError

class notef(ModelForm):
    # account = account
    # title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # created_date = date.today()
    # content = forms.CharField(max_length=1000, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # lock = forms.BooleanField()
    password = forms.CharField( widget=forms.PasswordInput, required=False)

    class Meta:
        model = Note
        fields = ('account','title', 'created_date', 'content', 'lock','password')

    def clean_password(self):
        lock = self.cleaned_data.get('lock', False)
        password = self.cleaned_data.get('password', None)

        if lock and password in EMPTY_VALUES:
            raise ValidationError("ENTER PASSWORD")

            # # validate the activity name
            # if password in EMPTY_VALUES:
            #     self._errors['password'] = self.error_class([
            #         'Enter a password'])            
        return password



