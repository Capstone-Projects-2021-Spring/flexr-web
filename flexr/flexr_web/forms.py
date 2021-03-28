from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

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
        ("School", "School"),
        ("Private", "Private"),
        ("Kids", "Kids"),
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


class PreferencesForm(ModelForm):
    class Meta:
        model = Account_Preferences
        # Make homepage a url field? may need to apppend https://www.
        fields = ('home_page', 'sync_enabled', 'searchable_profile', 'cookies_enabled', 'popups_enabled', 'is_dark_mode')

class FilterHistoryForm(forms.Form):
    site = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    start_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), required=False)
    start_time = forms.DateField(widget=forms.widgets.TimeInput(attrs={'type': 'time'}), required=False)
    end_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), required=False)
    end_time = forms.DateField(widget=forms.widgets.TimeInput(attrs={'type': 'time'}), required=False)

    class Meta:
        pass

class EditNoteForm(ModelForm):
    class Meta:
        model = Note
        # Make homepage a url field? may need to apppend https://www.
        fields = ('title', 'content')

class SharedFolder(ModelForm):
    class Meta:
        model = sharedFolder
        fields = ('title', 'description', 'collaborators', 'bookmarks', 'tabs', 'notes')

class BookmarkFolderForm(ModelForm):
    class Meta:
        model = bookmarkFolder
        fields = ('title', 'bookmarks')

class FilterBookmarkForm(forms.Form):
    start_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), required=False)
    start_time = forms.DateField(widget=forms.widgets.TimeInput(attrs={'type': 'time'}), required=False)
    end_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), required=False)
    end_time = forms.DateField(widget=forms.widgets.TimeInput(attrs={'type': 'time'}), required=False)

    class Meta:
        pass

class BookmarkOnFile(forms.Form):
    class Meta:
        model = bookmarkFolder
        fields = ('bookmarks')


