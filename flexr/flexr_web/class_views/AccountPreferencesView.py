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

from ..models import *
from ..forms import *
from ..serializers import *

@method_decorator(csrf_exempt, name='dispatch')
class AccountPreferencesAPIView(LoginRequiredMixin, DetailView):

    # not sure what the id is?
    # current account?
    # an id of an account?
    def get(self, request):
        curr_user = request.user
        curr_acc = curr_user.accounts.get(account_id = request.session['account_id'])
        acc_pref = curr_acc.account_preferences
        if (acc_pref == None):
            print("AccountPreferencesAPIView: get(): acc_pref was NONE!!!!")
            curr_acc.save()
        data = AccountPreferencesSerializer(acc_pref)
        return JsonResponse(data.data, safe=False)

    @method_decorator(csrf_exempt)
    def put(self, request):
        curr_user = request.user
        curr_acc = curr_user.accounts.get(account_id=request.session['account_id'])
        acc_pref = curr_acc.account_preferences
        if (acc_pref == None):
            print("AccountPreferencesAPIView: get(): acc_pref was NONE!!!!")
            curr_acc.save()
        request_data = json.loads(request.body)
        edit_home_url = request_data['home_page_url']
        print("AccountPreferencesAPIView: put(): edit_home_url: ",edit_home_url)
        if(curr_acc.sites.filter(url = edit_home_url).count() > 0):
            edit_home_site = curr_acc.sites.get(url = edit_home_url)
        else:
            edit_home_site = Site.objects.all(account = curr_acc, url = edit_home_url)
        print("AccountPreferencesAPIView: put(): edit_home_site: ", edit_home_site)
        acc_pref.home_page = edit_home_site[0]
        acc_pref.sync_enabled = request_data['sync_enabled']
        acc_pref.searchable_profile = request_data['searchable_profile']
        acc_pref.cookies_enabled = request_data['cookies_enabled']
        acc_pref.popups_enabled = request_data['popups_enabled']
        acc_pref.is_dark_mode = request_data['is_dark_mode']
        acc_pref.save()
        data = AccountPreferencesSerializer(acc_pref)
        return JsonResponse(data.data, safe=False)
