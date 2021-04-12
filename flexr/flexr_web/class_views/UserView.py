from django.contrib import messages
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

        if request.method == 'POST':
            data = request.POST.dict()
            email = data['email']
            username = data['username']
            password = data['password']

            user = User.objects.create_user(username, email, password)

            new_account = Account.objects.create(user=user, email=user.email, username = user.username)
            request.session['account_id'] = new_account.account_id
            site = Site.objects.create(account=self, url="https://google.com")
            site.save()
            new_account.account_preferences = Account_Preferences.objects.create(home_page = site)
            new_account.save()

            return JsonResponse({"success": f"User {username} created"})

            
        return JsonResponse({"error": f"Error creating user"})
        

    @method_decorator(csrf_exempt)
    def login(self, request, *args, **kwargs): 
        """
        Takes in a form and checks the database against the provided username and password to provide access to the app
            :param:
                request
            :return:
                JSONRequest with success or error message
        """
        if request.method == 'POST':
            data = request.POST.dict()
            username = data['username']
            password = data['password']

            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                data = UserSerializer(user)
                return JsonResponse(data.data, safe=False)

        return JsonResponse({"error": "Error logging in"})
        

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
            return JsonResponse({"success": f"User {user} logged out"})

        except:
            return JsonResponse({"error": "Error logging out"})

    @method_decorator(csrf_exempt)
    def check_status(self, request, *args, **kwargs):
        """
        Checks whether a user is logged in or not
            :param:
                request
            :return:
                JSONRequest with a logged in or logged out message
        """
        if request.method == 'GET':
            #print(request.session.__dict__)

            status = request.user.is_authenticated

            return JsonResponse(status, safe=False)

        return JsonResponse({"error": "error checking status"})