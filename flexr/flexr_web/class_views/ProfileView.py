from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

import pytz

from ..models import *
from ..forms import *

CHECKBOX_MAPPING = {'on':True,
                    None:False,}
                    
class ProfileView(LoginRequiredMixin, View):
    
    
    def get(self, *args, **kwargs):
        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id = self.request.session['account_id'])

        accounts = curr_user.accounts.all()
        acc_pref = curr_account.account_preferences
        # site = curr_account.sites.all()[0]
        # acc_pref.home_page = site

        pref_form = PreferencesForm()

        if curr_account.account_preferences.home_page is not None:
            pref_form.fields['home_page'].initial = curr_account.account_preferences.home_page

        else:

            try:
                # This isn't good for a first time user
                pref_form.fields['home_page'].initial = curr_account.sites.all()[0] 

            except:
                site = Site.objects.create(account = curr_account, url = "https://google.com")
                site.save()
                pref_form.fields['home_page'].initial = site

        # have to be sure to only show that user's sites!
        pref_form.fields['home_page'].queryset = curr_account.sites.all() 

        pref_form.fields['sync_enabled'].initial = curr_account.account_preferences.sync_enabled
        pref_form.fields['searchable_profile'].initial = curr_account.account_preferences.searchable_profile
        pref_form.fields['cookies_enabled'].initial = curr_account.account_preferences.cookies_enabled
        pref_form.fields['popups_enabled'].initial = curr_account.account_preferences.popups_enabled
        pref_form.fields['is_dark_mode'].initial = curr_account.account_preferences.is_dark_mode

        account_form = AccountForm()
        account_form.fields['username'].initial = curr_account.username
        account_form.fields['email'].initial = curr_account.email
        account_form.fields['phone_number'].initial = curr_account.phone_number
        account_form.fields['type_of_account'].initial = curr_account.type_of_account

        if ('message' in self.request.session):
            message = self.request.session['message']
            del self.request.session['message']
            messages.success(self.request, message)
        elif ('err_message' in self.request.session):
            message = self.request.session['err_message']
            del self.request.session['err_message']
            messages.error(self.request, message)

        return render(self.request, "flexr_web/profile.html", 
        {"current_account":curr_account, 
         "Accounts": accounts, 
         "Preferences":acc_pref, 
         "pref_form": pref_form, 
         "account_form": account_form})

    def edit_account(self, request, *args, **kwargs):
        
        acc = request.user.accounts.get(account_id=request.session['account_id'])
        # acc_pref = acc.account_preferences
        # acc_pref.delete()
        form = PreferencesForm(request.POST)
        # TODO add in checking for dashes!
        # This error below is gone bc I no longer check if form is valid
        #print(form.errors) # TODO <ul class="errorlist"><li>home_page<ul class="errorlist"><li>Account_ preferences with this Home page already exists.</li></ul></li></ul>

        home_page = request.POST.get('home_page')
        if(home_page == ''):
            #print("This is the fix")
            request.session['err_message'] = "Please select a homepage"

        acc_pref = acc.account_preferences
        home_page = acc.sites.get(id=home_page)
        acc_pref.home_page = home_page
        acc_pref.sync_enabled = CHECKBOX_MAPPING[request.POST.get('sync_enabled')]
        acc_pref.searchable_profile = CHECKBOX_MAPPING[request.POST.get('searchable_profile')]
        acc_pref.cookies_enabled = CHECKBOX_MAPPING[request.POST.get('cookies_enabled')]
        acc_pref.popups_enabled = CHECKBOX_MAPPING[request.POST.get('popups_enabled')]
        acc_pref.is_dark_mode = CHECKBOX_MAPPING[request.POST.get('is_dark_mode')]
        acc_pref.save()
        #print(acc_pref.sync_enabled)
        #print("acc_pref", acc_pref)
        request.session['message'] = "Account Preferences Saved"
        return redirect('/profile')


    def edit_account_preferences(self, request, *args, **kwargs):

        acc = request.user.accounts.get(account_id=request.session['account_id'])
        # acc_pref = acc.account_preferences
        # acc_pref.delete()
        form = PreferencesForm(request.POST)
        # TODO add in checking for dashes!
        # This error below is gone bc I no longer check if form is valid
        #print(form.errors) # TODO <ul class="errorlist"><li>home_page<ul class="errorlist"><li>Account_ preferences with this Home page already exists.</li></ul></li></ul>self.

        home_page = request.POST.get('home_page')
        if(home_page == ''):
            print("This is the fix")
            request.session['err_message'] = "Please select a homepage"

        acc_pref = acc.account_preferences
        home_page = acc.sites.get(id=home_page)
        acc_pref.home_page = home_page
        acc_pref.sync_enabled = CHECKBOX_MAPPING[request.POST.get('sync_enabled')]
        acc_pref.searchable_profile = CHECKBOX_MAPPING[request.POST.get('searchable_profile')]
        acc_pref.cookies_enabled = CHECKBOX_MAPPING[request.POST.get('cookies_enabled')]
        acc_pref.popups_enabled = CHECKBOX_MAPPING[request.POST.get('popups_enabled')]
        acc_pref.is_dark_mode = CHECKBOX_MAPPING[request.POST.get('is_dark_mode')]
        acc_pref.save()

        #print(acc_pref.sync_enabled)
        #print("acc_pref", acc_pref)

        request.session['message'] = "Account Preferences Saved"
        return redirect('/profile')
