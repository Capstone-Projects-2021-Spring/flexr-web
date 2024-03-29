from django.contrib import messages, auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import json
import pytz
import traceback

from ..models import *
from ..forms import *
from ..serializers import *


class UserAPIView(View):

    @method_decorator(csrf_exempt)
    def sign_up(self, request, *args, **kwargs):
        """
        Creates the User in the database, allowing them to sign in
            :param:
                request.POST that has the user information
            :return:
                JSONRequest with success and user data or error message
        """

        try:
            if request.method == 'POST':
                data = request.POST.dict()
                email = data['email']
                username = data['username']
                password = data['password']

                user = User.objects.create_user(username, email, password)
                user = auth.authenticate(username=username, password=password)
                if user is not None and user.is_active:
                    auth.login(request, user)
                    new_account = Account.objects.create(user=user, email=user.email, username = user.username)
                    request.session['account_id'] = new_account.account_id
                    site = Site.objects.create(account=new_account, url="https://google.com")
                    site.save()
                    new_account.account_preferences = Account_Preferences.objects.create(home_page = site)
                    new_account.save()

                    print("UserAPIView: logout(): user", new_account, " Message: USER SIGNED UP")
                    data = AccountSerializer(new_account)
                    return JsonResponse(data.data, safe=False)
            return JsonResponse({"error": f"Error creating user"})

        except Exception as e:
            return JsonResponse({ "error": str(e), "traceback": traceback.extract_tb(e.__traceback__).format() }, status=500) 
        

    @method_decorator(csrf_exempt)
    def login(self, request, *args, **kwargs): 
        """
        Takes in a form and checks the database against the provided username and password to provide access to the app
            :param:
                request
            :return:
                JSONRequest with success or error message
        """
        try:
            if request.method == 'POST':
                data = request.POST.dict()
                username = data['username']
                password = data['password']

                user = authenticate(username=username, password=password)

                if user:
                    login(request, user)
                    data = UserSerializer(user)
                    print("UserAPIView: login(): user", user, " Message: USER LOGGED IN")
                    return JsonResponse(data.data, safe=False)
            return JsonResponse({"error": "Error logging in"}, status = 404)
            
        except Exception as e:
            return JsonResponse({ "error": str(e), "traceback": traceback.extract_tb(e.__traceback__).format() }, status=500) 
        

    @method_decorator(csrf_exempt)
    def logout(self, request, *args, **kwargs):
        """
        Logs the user out of flexr. Erases session data and does not allow access
            :param:
                request
            :return:
                JSONRequest with success or error message
        """

        try:
            user = request.user
            logout(request)
            print("UserAPIView: logout(): user", user, " Message: USER LOGGED OUT")
            return JsonResponse({"success": f"User {user} logged out"})

        except Exception as e:
            return JsonResponse({ "error": str(e), "traceback": traceback.extract_tb(e.__traceback__).format() }, status=500) 

    @method_decorator(csrf_exempt)
    def check_status(self, request, *args, **kwargs):
        """
        Checks whether a user is logged in or not
            :param:
                request
            :return:
                JSONRequest with a logged in or logged out message
        """

        try:
            if request.method == 'GET':
                #print(request.session.__dict__)

                status = request.user.is_authenticated

                return JsonResponse(status, safe=False)

            return JsonResponse({"error": "error checking status"})
        
        except Exception as e:
            return JsonResponse({ "error": str(e), "traceback": traceback.extract_tb(e.__traceback__).format() }, status=500) 