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
    
    def get(self, *args, **kwargs):
        pass

    def add_account(self, request, *args, **kwargs):

        form = AccountForm(request.POST)

        if form.is_valid():
        
            username = request.POST.get('username')
            #print(username)
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            type_of_account = request.POST.get("type_of_account")

            new_account = Account.objects.create(user=request.user, email=email, username = username, phone_number = phone_number, type_of_account = type_of_account)

            new_account.save() # not needed ?

            request.session['account_id'] = new_account.account_id
            request.session['message'] = "Account Created"

            return redirect('/')

    # Gerald: is this decorator stil required?
    @csrf_exempt
    def switch_account(self, request,*args, **kwargs):

    
        try:
            request.user.accounts.get(account_id = kwargs["id"])
            #print("switching account....")
            request.session['message'] = "Account Switched"
            request.session['account_id'] = kwargs["id"]
        except:
            #print("error switching account....")
            request.session['err_message'] = "Error switching account"

        return redirect('/')