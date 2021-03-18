from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

import pytz

from ..models import *
from ..forms import *


class BookmarksView(LoginRequiredMixin, View):
    
    
    def get(self, *args, **kwargs):

        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id = self.request.session['account_id'])
        bookmarks = curr_account.bookmarks.all()

        if ('message' in self.request.session):
            message = self.request.session['message']
            del self.request.session['message']
            messages.success(self.request, message)

        elif ('err_message' in self.request.session):
            message = self.request.session['err_message']
            del self.request.session['err_message']
            messages.error(self.request, message)

        return render(self.request, "flexr_web/bookmarks.html", {"Bookmarks": bookmarks})

    def add_bookmark(self, request, *args, **kwargs):

        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

        accounts = curr_user.accounts.all()
        tabs = curr_account.tabs.all()

        tab = curr_account.tabs.get(pk = kwargs['id'])
        Bookmark.create_bookmark(tab, curr_account)
        request.session['message'] = "Bookmark Created"

        return redirect('/open_tabs')


    def delete_bookmark(self, request, *args, **kwargs):

        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

        Bookmark.delete_bookmark(kwargs['id'])
        request.session['message'] = "Bookmark Deleted"
        
        return redirect('/bookmarks')