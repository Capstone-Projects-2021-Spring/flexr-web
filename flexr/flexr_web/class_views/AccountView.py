import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView
from django.http import HttpResponse, JsonResponse

import pytz
import traceback

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
            return redirect(request.session['redirect_url'])

    # Gerald: is this decorator stil required?
    @csrf_exempt
    def switch_account(self, request, *args, **kwargs):
        """
        Switch to a different account the current user owns
        """
    
        try:

            # get account to switch to
            request.user.accounts.get(account_id = kwargs["id"])
            print("AccountViewWeb.switch_account(): requested account: ", request.user.accounts.get(account_id = kwargs["id"]))
            # switch account id and message of the session
            request.session['message'] = "Account Switched"
            if ("account_id" in request.session):
                del request.session['account_id']
            request.session['account_id'] = kwargs["id"]

        except:
            # no account found with requested account id
            request.session['err_message'] = "Error switching account"

        # return to index page
        return redirect(request.session['redirect_url'])

    def delete(self, request, pk):
        curr_user = request.user
        if (curr_user.accounts.all().count() > 1):
            if (request.session['account_id'] == pk):
                curr_account = curr_user.accounts.get(account_id=request.session['account_id'])
                curr_account.delete()
                
            else:
                del_account = curr_user.accounts.get(account_id=pk)
                del_account.delete()
            new_curr_account = curr_user.accounts.all()[0]
            request.session['account_id'] = new_curr_account.account_id
            request.session['message'] = "Account deleted"
            return redirect(request.session['redirect_url'])
        else:
            request.session['err_message'] = "Can't delete your only account"
            return redirect(request.session['redirect_url'])

@method_decorator(csrf_exempt, name='dispatch')
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
        try:
            curr_user = request.user

            account = Account.objects.get(account_id = kwargs['id'])

            data = AccountSerializer(account)
            return JsonResponse(data.data, safe=False)
        
        except Exception as e:
            return JsonResponse({ "error": str(e), "traceback": traceback.extract_tb(e.__traceback__).format() }, status=500)

    def get_all(self, request, *args, **kwargs):
        try:
            curr_user = request.user

            accounts = curr_user.accounts.all()

            data = AccountSerializer(accounts, many = True)
            return JsonResponse(data.data, safe=False)

        except Exception as e:
            return JsonResponse({ "error": str(e), "traceback": traceback.extract_tb(e.__traceback__).format() }, status=500)

    @method_decorator(csrf_exempt)
    def switch_account(self, request, *args, **kwargs):
        try:
            curr_user = request.user
            if(curr_user.accounts.filter(account_id = kwargs['id']).count() == 1):
                request.session['account_id'] = kwargs['id']
                print("AccountViewAPI.switch_account(): requested account: "+str(kwargs['id'])+" Message : Account switched")
                return JsonResponse({"status": "account switched"})
                # need to return some json
            else:
                print("AccountViewAPI.switch_account(): requested account: " + str(
                    kwargs['id']) + " ERROR MESSAGE : account does not exist for that user with that id")
                return JsonResponse({"error": "account does not exist for that user with that id"})
                # need to return some json here 404 or 403

        except Exception as e:
            return JsonResponse({ "error": str(e), "traceback": traceback.extract_tb(e.__traceback__).format() }, status=500)


    @method_decorator(csrf_exempt)
    def delete(self, request , *args, **kwargs):
        try:
            curr_user = request.user
            if(curr_user.accounts.all().count() > 1):
                if(request.session['account_id'] == kwargs['id']):
                    curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
                    curr_account.delete()
                    new_curr_account =  curr_user.accounts.all()[0]
                    request.session['account_id'] = new_curr_account.account_id
                else:
                    del_account = curr_user.accounts.get(account_id =  kwargs['id'])
                    del_account.delete()
                return JsonResponse({"success": "Account deleted"})
            else:
                return JsonResponse({"error": "User only has 1 account and can not be deleted"})

        except Exception as e:
            return JsonResponse({ "error": str(e), "traceback": traceback.extract_tb(e.__traceback__).format() }, status=500)

    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            curr_user = request.user
            data = json.loads(request.body)

            new_account = Account.objects.create(user = curr_user, )
            new_account.save()
            data = AccountSerializer(new_account)
            return JsonResponse(data.data, safe=False)
        
        except Exception as e:
            return JsonResponse({ "error": str(e), "traceback": traceback.extract_tb(e.__traceback__).format() }, status=500)

    @method_decorator(csrf_exempt)
    def put(self, request, *args, **kwargs):
        curr_user = request.user
        data = json.loads(request.body)
        try:
            edit_acc = curr_user.accounts.get(account_id = kwargs['id'])
            edit_acc.username = data['username']
            edit_acc.email = data['email']
            edit_acc.phone_number = data['phone_number']
            edit_acc.type_of_account = data["type_of_account"]
            edit_acc.save()
            data = AccountSerializer(edit_acc)
            return JsonResponse(data.data, safe=False)
        except:
            return JsonResponse({"error": "Account doesn't exist for this user"})
