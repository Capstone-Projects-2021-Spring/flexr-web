from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import pytz
import traceback

from ..models import *
from ..forms import *
from ..serializers import SiteSerializer


@method_decorator(csrf_exempt, name='dispatch')
class SiteAPIView(LoginRequiredMixin, View):

    def get(self, request):
        try:
            curr_account = request.user.accounts.get(account_id = request.session['account_id'])
            print("SiteAPIView: get(): request.GET.get('url')", request.GET.get("url"))
            site = curr_account.sites.get(url = request.GET.get('url') )
            data = SiteSerializer(site)
            return JsonResponse(data.data, safe=False)
        except Exception as e:
            return JsonResponse({ "error": str(e), "traceback": traceback.extract_tb(e.__traceback__).format() }, status=500)

    def post(self, request):
        try:
            curr_user = request.user
            curr_account = curr_user.accounts.get(account_id=request.session['account_id'])

            url = request.POST.get('url')
            site, created = Site.objects.get_or_create(account = curr_account, url = url)
            site.save()

            data = SiteSerializer(site)
            return JsonResponse(data.data, safe=False)

        except Exception as e:
            return JsonResponse({ "error": str(e), "traceback": traceback.extract_tb(e.__traceback__).format() }, status=500)

    def put(self):
        pass

    # not going to have this as an option
    def delete(self):
        pass
