from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View

import json
import pytz

from ..models import *
from ..forms import *
from ..serializers import *

class TabsView(LoginRequiredMixin, View):
    """
    View class for the tabs page
    """

    def get(self, *args, **kwargs):
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
        return redirect('/')

    

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
        return redirect('/open_tabs')




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
            
        return redirect('/')

@method_decorator(csrf_exempt, name='dispatch')
class TabsViewAPI(LoginRequiredMixin, DetailView):

    def get_queryset(self):
        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id= self.request.session['account_id'])
        return Tab.objects.filter(account = curr_account)

    # This method is used to get a single tab
    def get(self, *args, **kwargs):
        """
        Looks in the tab table for the instance. If it's not there then it deletes it
                  :param:
                      request.GET has tab id or url
                  :return:
                      JSONRequest with tab data
        """

        curr_account = Account.objects.filter(user = self.request.user)[0]
        #message = Tab.visit_tab(kwargs["id"], curr_account)
        tabs = curr_account.tabs.all()
        data = TabSerializer(tabs, many=True)
        return JsonResponse(data.data, safe=False)
        

    # This method is used to close a tab
    def delete(self, request, *args, **kwargs):
        """
        Closes a specifc tab, deletes from tab table
                  :param:
                      request.DELETE has the tab id
                  :return:
                      JSONRequest with success or error message
        """
        tab = self.get_queryset().filter(pk = kwargs["id"])[0]
        
        #curr_user = request.user
        #curr_account = curr_user.accounts.get(account_id= request.session['account_id'])
        #tab = Tab.objects.filter(account = curr_account).filter(pk = kwargs["id"])
        tab.delete()
        return HttpResponse("worked")

    def post(self, request, *args, **kwargs):
        """
       Looks in the site table for an instance; uses that instance or creates a new one if one doesn't exist to
       create a tab instance in the tab table
                 :param:
                     request.PUT has information for a tab like url
                 :return:
                     JSONRequest with success or error message
       """
        #print(self.request.session)
        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id=self.request.session['account_id'])
        message = "sucess"
        site_url = request.POST.get("url")
        print(request.POST)
        tab = Tab.open_tab(site_url = site_url, curr_account= curr_account)
        return HttpResponse(message)


    def put(self, request, *args, **kwargs):
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

        data = json.loads(request.body)
        result = Tab.objects.filter(pk = kwargs["id"]).update(**data)

        return HttpResponse(f'Tab object edited')