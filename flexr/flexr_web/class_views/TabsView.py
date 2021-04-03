from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import traceback
import pytz
import json
from ..models import *
from ..forms import *
from ..serializers import TabSerializer


class TabsView(LoginRequiredMixin, View):
    """
    View class for the tabs page
    """

    def get(self,request, *args, **kwargs):
        """
        Display the tabs page
        """

        # get the current user and current account
        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id = self.request.session['account_id'])

        # get all accounts for current user and
        # get all tabs for current account
        accounts = curr_user.accounts.all()
        tabs = curr_account.tabs.all()

        # request messages for debugging
        if ('message' in self.request.session):
            message = self.request.session['message']
            del self.request.session['message']
            messages.success(self.request, message)

        elif ('err_message' in self.request.session):
            message = self.request.session['err_message']
            del self.request.session['err_message']
            messages.error(self.request, message)
        request.session['prev_url'] = '/open_tabs/'
        # display the page
        return render(self.request, "flexr_web/open_tabs.html", 
        {"Tabs":tabs, 
        "Accounts": accounts})

    def add_tab(self, request, *args, **kwargs):
        """
        Add a tab to the current account
        """

        # get the current user and current account
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id= request.session['account_id'])


        # get site url
        site_url = request.POST.get("url")
        
        # open the requested tab
        tab = Tab.open_tab(site_url = site_url, curr_account=curr_account)

        # request message for debugging
        request.session['message'] = "Tab added"

        # return to index page
        return redirect(request.session['prev_url'])

    

    def close_tab(self, request, *args, **kwargs):
        """
        Close a tab for the current account
        """

        # get the current user and current account
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id=request.session['account_id'])


        try:
            # try to close requested tab
            tab = curr_account.tabs.get(id = kwargs['id'])
            tab = Tab.close_tab( tabID = kwargs['id'], curr_account = curr_account)
            request.session['message'] = "Tab closed"

        except:
            # tab not found
            request.session['err_message'] = "Tab could not be closed"

        # TODO we should set up django sesions to know where to redirect a user based on previous page
        return redirect(request.session['prev_url'])




    def open_tab(self, request, *args, **kwargs):
        """
        Gerald: This seems to do the same thing as self.add_tab
        but I keep it just incase
        """
        
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id=request.session['account_id'])
        
        try:

            site_url = curr_account.sites.get(id = kwargs['id']).url
            tab = Tab.open_tab(site_url=site_url, curr_account=curr_account)
            request.session['message'] = "Tab added"

        except:
            request.session['err_message'] = "Tab could not be opened"
            
        return redirect(request.session['prev_url'])

@method_decorator(csrf_exempt, name='dispatch')
class TabAPIView(View):

    def get(self, request, *args, **kwargs):
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

        url = request.path.split('/')

        if not url[-1]:
            url = url[:-1]

        if url[-1] == 'tabs':
            return self.get_all_tabs(request, *args, **kwargs)
        else:
            return self.get_tab(request, *args, **kwargs)


    def get_tab(self, request, *args, **kwargs):
        curr_user = request.user
        current_account = curr_user.accounts.get(account_id = request.session['account_id'])

        tab = current_account.tabs.get(id = kwargs['id'])

        data = TabSerializer(tab)
        return JsonResponse(data.data, safe=False)

    def get_all_tabs(self, request, *args, **kwargs):
        curr_user = request.user
        current_account = curr_user.accounts.get(account_id = request.session['account_id'])

        tabs = current_account.tabs.all()

        data = TabSerializer(tabs, many = True)
        return JsonResponse(data.data, safe=False)

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        """
        Add a tab to the current account
        """

        # get the current user and current account
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id=request.session['account_id'])

        # get site url
        data = json.loads(request.body)
        site_url = data["url"]

        try:
            tab = Tab.open_tab(site_url=site_url, curr_account=curr_account)

            if isinstance(tab, Exception):
                return JsonResponse({ "error": str(tab), "traceback": traceback.extract_tb(tab.__traceback__).format() }, status=500)

            data = TabSerializer(tab)
            return JsonResponse(data.data, safe=False)

        except Exception as e:
            return JsonResponse({ "error": str(e), "traceback": traceback.extract_tb(e.__traceback__).format() }, status=500)

    @method_decorator(csrf_exempt)
    def delete(self, request, *args, **kwargs):
        """
        Close a tab for the current account
        """

        # get the current user and current account
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id=request.session['account_id'])

        # try:
            # try to close requested tab
        print(kwargs['id'])
        tab = Tab.close_tab(tabID=kwargs['id'], curr_account=curr_account)

        if isinstance(tab, Exception):
            return JsonResponse({ "error": str(tab), "traceback": traceback.extract_tb(tab.__traceback__).format() }, status=500)
        
        print("TabAPI: Delete: close tab return", tab)
        return JsonResponse({"success": "tab closed"})
        # except:
        #     return JsonResponse({"error": "Could not close tab"}, status = 400)

    # @method_decorator(csrf_exempt)
    # def edit_tab(self, request, *args, **kwargs):
    #     # get the current user and current account
    #     curr_user = request.user
    #     curr_account = curr_user.accounts.get(account_id=request.session['account_id'])
    #
    #     data = json.loads(request.body)
    #
    #     if 'url' in data:
    #         site = Site.objects.get_or_create(account = curr_account, url = data['url'])[0]
    #         data['site_id'] = site.id
    #
    #     result = Tab.objects.filter(pk = kwargs["id"]).update(**data)
    #
    #     return JsonResponse({"success": "tab edited"})

    @method_decorator(csrf_exempt)
    def visit_tab(self, request, *args, **kwargs):
        """
        Gerald: This seems to do the same thing as self.add_tab
        but I keep it just incase
        """

        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id=request.session['account_id'])

        tab = Tab.visit_tab(tabID=kwargs['id'], curr_account=curr_account)

        if isinstance(tab, Exception):
            return JsonResponse({ "error": str(tab), "traceback": traceback.extract_tb(tab.__traceback__).format() }, status=500)
            
        data = TabSerializer(tab)
        return JsonResponse(data.data, safe=False)