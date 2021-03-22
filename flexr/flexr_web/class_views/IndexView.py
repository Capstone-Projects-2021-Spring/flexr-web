from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from ..models import *
from ..forms import *

# TODO: Gerald add the other functionality
# TODO: Gerald refractor out common code like request messages
# TODO: Gerald connect class based views to their html page
# TODO: Gerald fix broken view tests 
class IndexView(LoginRequiredMixin, View):
    """
    View class for the index/home page
    """
    def get(self, *args, **kwargs):
        """
        Display the index/home page
        """

        # get current user
        curr_user = self.request.user

        # try to get current account
        try:
            print("IndexView curr_user")
            curr_account = curr_user.accounts.get(account_id = self.request.session['account_id'])
            # print("IndexView: Account Successfully Switched: "+ str(curr_account))
            curr_account.rank_sites()
        # if no current account found, set current account to
        # first account for the current user
        except:
            curr_account = curr_user.accounts.all()[0]
            self.request.session['account_id'] = curr_account.account_id
            curr_account.rank_sites()
            # print("IndexView: Account initialized:" )

        # grab all models for the current user
        # and the current account
        accounts = curr_user.accounts.all()
        history = curr_account.history.all()
        sites = curr_account.sites.all()
        tabs = curr_account.tabs.all()
        bookmarks = curr_account.bookmarks.all()
        notes = curr_account.notes.all()
        folders = curr_account.shared_folders.all()
        suggested_sites = curr_account.suggested_sites.order_by('-site_ranking')
        # suggested_sites = curr_account.suggested_sites()

        print(curr_user)

        # request messages for debugging
        if ('message' in self.request.session):
            message = self.request.session['message']
            del self.request.session['message']
            messages.success(self.request, message)
        elif('err_message' in self.request.session):
            message = self.request.session['err_message']
            del self.request.session['err_message']
            messages.error(self.request, message)


        # get account form object
        form = AccountForm

        # display the page
        return render(self.request, "flexr_web/index.html",
                      {"curr_acc": curr_account, 
                       "Accounts": accounts, 
                       "Sites": sites,
                       "Suggested_Sites": suggested_sites,
                       "Tabs": tabs, 
                       "Notes": notes,
                       "History": history, 
                       "Bookmarks": bookmarks, 
                       "Folders":folders,
                       "form": form})