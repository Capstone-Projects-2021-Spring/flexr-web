from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.db.models import Q
from itertools import chain

import pytz

from ..models import *
from ..forms import *

# helper for determining if a checkbox is selected or not
CHECKBOX_MAPPING = {'on':True,
                    None:False,}
                    
class ProfileView(LoginRequiredMixin, View):
    """
    View class for the profile page
    """
    
    
    def get(self, *args, **kwargs):
        """
        Display the profile page
        """

        # get current user and current account
        curr_user = self.request.user
        
        # get all accounts for the user and
        # account preferrences for the users
        print(curr_user)
        curr_account = curr_user.accounts.get(account_id=self.request.session['account_id'])
        print(curr_account)

        accounts = curr_user.accounts.all()
        acc_pref = curr_account.account_preferences

        # site = curr_account.sites.all()[0]
        # acc_pref.home_page = site

        # get form object for preferences
        pref_form = PreferencesForm()

        # set form data for home page if exists
        if curr_account.account_preferences.home_page is not None:
            pref_form.fields['home_page'].initial = curr_account.account_preferences.home_page

        
        else:
            # otherwise try to set to first site found for the user
            try:
                # This isn't good for a first time user
                pref_form.fields['home_page'].initial = curr_account.sites.all()[0] 

            # worst case scenario no sites found and set to google
            except:
                site = Site.objects.create(account=curr_account, url="https://google.com")
                site.save()
                pref_form.fields['home_page'].initial = site

        # have to be sure to only show that user's sites!
        pref_form.fields['home_page'].queryset = curr_account.sites.all() 

        # populate initial form data from current account's preferences

        pref_form.fields['sync_enabled'].initial = curr_account.account_preferences.sync_enabled
        pref_form.fields['searchable_profile'].initial = curr_account.account_preferences.searchable_profile
        pref_form.fields['cookies_enabled'].initial = curr_account.account_preferences.cookies_enabled
        pref_form.fields['popups_enabled'].initial = curr_account.account_preferences.popups_enabled
        pref_form.fields['is_dark_mode'].initial = curr_account.account_preferences.is_dark_mode

        # get form object and
        # populate it with account information
        account_form = AccountForm()
        account_form.fields['username'].initial = curr_account.username
        account_form.fields['email'].initial = curr_account.email
        account_form.fields['phone_number'].initial = curr_account.phone_number
        account_form.fields['type_of_account'].initial = curr_account.type_of_account
        print("hello")

        # request messages for debugging
        if ('message' in self.request.session):
            message = self.request.session['message']
            del self.request.session['message']
            messages.success(self.request, message)
        elif ('err_message' in self.request.session):
            message = self.request.session['err_message']
            del self.request.session['err_message']
            messages.error(self.request, message)

        # display the profile page
        return render(self.request, "flexr_web/profile.html", 
        {"current_account":curr_account, 
         "Accounts": accounts, 
         "Preferences":acc_pref, 
         "pref_form": pref_form, 
         "account_form": account_form})

    def edit_account(self, request, *args, **kwargs):
        """
        Edit an account
        """
        
        # grab form object
        form = AccountForm(request.POST)

        #print(form.errors)

        # check that form is valid
        if form.is_valid():
            # grab account information from the form
            username = request.POST.get('username')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            type_of_account = request.POST.get("type_of_account")
            account = Account.objects.get(account_id = request.session['account_id'])
            #print(account)

            # update account information based on the form data
            account.username = username
            account.email=email
            account.phone_number = phone_number
            account.type_of_account = type_of_account
            account.save()

            # messages.add_message(request, , 'A serious error occurred.')
            #TODO make sure that we error check everything

            # request message for debugging
            request.session['message'] = "Account Edited"

            # return to profile page
            return redirect('/profile')
          
        friends = curr_account.all_friends.all()
        friend_requests = curr_account.to_friend.all().filter(status="Pending")
        print("friend requests", friend_requests)
        pending_friends = curr_account.all_pending_friends.all()
        print(pending_friends)
        all_accounts =  Account.objects.filter(~Q(account_id__in=[o.account_id for o in accounts])) #this needs to be filter on account preferences searchable
        # all_accounts = accounts
        print(all_accounts)
        return render(self.request, "flexr_web/profile.html", {"curr_acc": curr_account, "Accounts": accounts,
                                                          "Preferences": acc_pref, "pref_form": pref_form,
                                                          "account_form": account_form, "Friends": friends,
                                                          "AllAccounts": all_accounts,
                                                          "friend_requests": friend_requests})



    def edit_account_preferences(self, request, *args, **kwargs):
        """
        Edit an account's preferences 
        """

        # get current account for the user and the form object
        acc = request.user.accounts.get(account_id=request.session['account_id'])
        form = PreferencesForm(request.POST)
        # acc_pref = acc.account_preferences
        # acc_pref.delete()
        # TODO add in checking for dashes!
        # This error below is gone bc I no longer check if form is valid
        #print(form.errors) # TODO <ul class="errorlist"><li>home_page<ul class="errorlist"><li>Account_ preferences with this Home page already exists.</li></ul></li></ul>

        # attempt to get home page for the account
        home_page = request.POST.get('home_page')
        if(home_page == ''):
            #print("This is the fix")
            request.session['err_message'] = "Please select a homepage"


        # update account preferences based on the form
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

        # request message for debugging 
        request.session['message'] = "Account Preferences Saved"

        # return to profile page
        return redirect('/profile')
