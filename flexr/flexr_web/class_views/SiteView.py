from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View

import pytz

from ..models import *
from ..forms import *
from ..serializers import SiteSerializer


class SiteAPIView(LoginRequiredMixin, View):

    def get(self, request):
        curr_account = request.user.accounts.get(account_id = request.session['account_id'])
        print(request.GET.get("url"))
        site = curr_account.sites.get(url = request.GET.get('url') )
        data = SiteSerializer(site)
        return JsonResponse(data.data, safe=False)

    def post(self, request):
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id=request.session['account_id'])

        url = request.POST.get('url')
        site = Site.objects.get_or_create(account = curr_account, url = url)
        site.save()
        data = SiteSerializer(site)
        return JsonResponse(data.data, safe=False)

    def put(self):
        pass

    # not going to have this as an option
    def delete(self):
        pass
