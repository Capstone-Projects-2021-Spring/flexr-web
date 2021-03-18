from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

import pytz

from ..models import *
from ..forms import *


class BookmarksView(LoginRequiredMixin, View):
    """
    View class for the bookarks page
    """
    
    def get(self, *args, **kwargs):
        """
        Display the bookmarks page
        """

        # get current user and current account
        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id = self.request.session['account_id'])

        # get all bookmarks for current user
        bookmarks = curr_account.bookmarks.all()

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
        return render(self.request, "flexr_web/bookmarks.html", 
        {"Bookmarks": bookmarks})

    def add_bookmark(self, request, *args, **kwargs):
        """
        Add a bookmark to the current account from a tab
        """

        # get current user and current account
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

        # get all accounts and all tabs for the user
        accounts = curr_user.accounts.all()
        tabs = curr_account.tabs.all()

        # get requested tab object
        tab = curr_account.tabs.get(pk = kwargs['id'])

        # create requested bookmark object
        Bookmark.create_bookmark(tab, curr_account)

        # request message for debugging
        request.session['message'] = "Bookmark Created"

        # go to open_tabs page
        return redirect('/open_tabs')


    def delete_bookmark(self, request, *args, **kwargs):
        """
        Delete a bookmark from the current account
        """

        # get current user and current account
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

        # delete requested bookmark
        Bookmark.delete_bookmark(kwargs['id'])

        # request message for debugging
        request.session['message'] = "Bookmark Deleted"
        
        # return to bookmarks page
        return redirect('/bookmarks')