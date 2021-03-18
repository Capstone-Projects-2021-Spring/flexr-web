from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

import pytz

from ..models import *
from ..forms import *

class TabsView(LoginRequiredMixin, View):
    """
    View class for the tabs page
    """

    def get(self, *args, **kwargs):

        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id = self.request.session['account_id'])

        accounts = curr_user.accounts.all()
        tabs = curr_account.tabs.all()

        if ('message' in self.request.session):
            message = self.request.session['message']
            del self.request.session['message']
            messages.success(self.request, message)

        elif ('err_message' in self.request.session):
            message = self.request.session['err_message']
            del self.request.session['err_message']
            messages.error(self.request, message)


        return render(self.request, "flexr_web/open_tabs.html", 
        {"Tabs":tabs, 
        "Accounts": accounts})

    def add_tab(self, request, *args, **kwargs):

        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id= request.session['account_id'])

        message = ""
        site_url = request.POST.get("url")
        
        tab = Tab.open_tab(site_url = site_url, curr_account=curr_account)
        request.session['message'] = "Tab added"

        return redirect('/')

    def open_tab(self, request, *args, **kwargs):
        
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id=request.session['account_id'])

        message = ""
        
        try:

            site_url = curr_account.sites.get(id = kwargs['id']).url
            tab = Tab.open_tab(site_url=site_url, curr_account=curr_account)
            request.session['message'] = "Tab added"

        except:
            request.session['err_message'] = "Tab could not be opened"
            
        return redirect('/')

    def close_tab(self, request, *args, **kwargs):

        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id=request.session['account_id'])

        message = ""

        try:

            tab = curr_account.tabs.get(id = kwargs['id'])
            tab = Tab.close_tab( tabID = kwargs['id'], curr_account = curr_account)
            request.session['message'] = "Tab closed"

        except:

            request.session['err_message'] = "Tab could not be closed"

        # TODO we should set up django sesions to know where to redirect a user based on previous page
        return redirect('/') 


    def post(self, *args, **kwargs):
        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id = self.request.session['account_id'])

        accounts = curr_user.accounts.all()
        tabs = curr_account.tabs.all()

        tab = curr_account.tabs.get(pk = kwargs['id'])
        Bookmark.create_bookmark(tab, curr_account)
        request.session['message'] = "Bookmark Created"

        return redirect('/open_tabs')

    def delete(self, *args, **kwargs):
        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id=self.request.session['account_id'])

        message = ""
        
        try:
            tab = curr_account.tabs.get(id = kwargs['id'])
            tab = Tab.close_tab( tabID = kwargs['id'], curr_account = curr_account)
            request.session['message'] = "Tab closed"

        except:
            request.session['err_message'] = "Tab could not be closed"

        # TODO we should set up django sesions to know where to redirect a user based on previous page
        return redirect('/') 