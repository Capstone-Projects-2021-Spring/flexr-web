from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView

import pytz

from ..models import *
from ..forms import *

# TODO: Gerald add request messages
# TODO: Gerald add comments

# TODO implement request messages for every call to change something in database
    #This will be usefull for testing

# Gerald: Do we need DetailView ?
class AccountView(LoginRequiredMixin, DetailView):
    """
    View class for the account management
    """
    
    # Gerald: no Account page so we don't 
    # need to display anything
    def get(self, *args, **kwargs):
        pass

    def add_account(self, request, *args, **kwargs):
        """
        Add an account to the current user
        """

        # get account form object on the page
        form = AccountForm(request.POST)

        # check form is valid
        if form.is_valid():
        
            # grab account information from form
            username = request.POST.get('username')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            type_of_account = request.POST.get("type_of_account")

            # create Account object
            new_account = Account.objects.create(user=request.user, email=email, username = username, phone_number = phone_number, type_of_account = type_of_account)

            # not needed ?
            # this should also create the object
            new_account.save() 

            # set up request sessions for account
            request.session['account_id'] = new_account.account_id
            request.session['message'] = "Account Created"

            # return to index page
            return redirect('/')

    # Gerald: is this decorator stil required?
    @csrf_exempt
    def switch_account(self, request, *args, **kwargs):
        """
        Switch to a different account the current user owns
        """
    
        try:

            # get account to switch to
            request.user.accounts.get(account_id = kwargs["id"])

            # switch account id and message of the session
            request.session['message'] = "Account Switched"
            request.session['account_id'] = kwargs["id"]

        except:
            # no account found with requested account id
            request.session['err_message'] = "Error switching account"

        # return to index page
        return redirect('/')