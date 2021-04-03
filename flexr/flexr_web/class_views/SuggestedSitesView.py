from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import pytz

from ..models import *
from ..forms import *
from ..serializers import SiteSerializer

class SuggestedSiteAPIView(LoginRequiredMixin, View):

    def get(self, request):
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

        suggested_sites = curr_account.suggested_sites.order_by('-site_ranking')

        data = SiteSerializer(suggested_sites, many=True)
        return JsonResponse(data.data, safe=False)