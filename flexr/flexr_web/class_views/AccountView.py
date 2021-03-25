from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView
from django.http import HttpResponse, JsonResponse

import pytz

from ..models import *
from ..forms import *
from ..serializers import *

# TODO: Gerald add request messages
# TODO: Gerald add comments

# TODO implement request messages for every call to change something in database
    #This will be usefull for testing

# Gerald: Do we need DetailView ?
class AccountViewWeb(LoginRequiredMixin, DetailView):
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
            print("Requested accounts",request.user.accounts.get(account_id = kwargs["id"]))
            # switch account id and message of the session
            request.session['message'] = "Account Switched"
            if ("account_id" in request.session):
                del request.session['account_id']
            request.session['account_id'] = kwargs["id"]

        except:
            # no account found with requested account id
            request.session['err_message'] = "Error switching account"

        # return to index page
        return redirect('/')


class AccountViewAPI(LoginRequiredMixin, DetailView):
    """This is for a detail view of a single account"""

    def get(self, request, *args, **kwargs):
        """This returns the user's current account"""

        url = request.path.split('/')

        if url[-2] == 'accounts':
            return self.get_all(request, *args, **kwargs)
        else:
            return self.get_account(request, *args, **kwargs)

    def get_account(self, request, *args, **kwargs):
        curr_user = request.user
        current_account = curr_user.accounts.get(account_id = request.session['account_id'])


        account = Account.objects.filter(pk = kwargs['id'])

        data = AccountSerializer(account)
        return JsonResponse(data.data, safe=False)

    def get_all(self, request, *args, **kwargs):
        curr_user = request.user
        current_account = curr_user.accounts.get(account_id = request.session['account_id'])

        accounts = curr_user.accounts.all()

        data = AccountSerializer(accounts, many = True)
        return JsonResponse(data.data, safe=False)




    def switch_account(self, request, pk):
        curr_user = request.user
        if(curr_user.accounts.filter(account_id = pk).count() == 1):
            request.session['account_id'] = pk
            print("Account View API: account switched")
            return HttpResponse(status=200)
            # need to return some json
        else:
            print("Account View API: account does not exist for that user with that id")
            return HttpResponse(status = 404)
            # need to return some json here 404 or 403

    # This needs to be POST
    # def edit_account(self, request):
    #     curr_user = request.user
    #     curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

