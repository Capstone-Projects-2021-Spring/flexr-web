from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import json
import pytz

from ..models import *
from ..forms import *
from ..serializers import BookmarkSerializer


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

@method_decorator(csrf_exempt, name='dispatch')
class BookmarksViewAPI(LoginRequiredMixin, DetailView):

    def post(self, request, *args, **kwargs):
        """
            Adds a bookmark to a bookmark table for the specific account
                    Parameters:
                        request.PUT has a form for data for a bookmark
                    Returns:
                        JSONRequest with success or error message
        """

        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

        data = request.POST.dict()
        bookmark = Bookmark.objects.create(account=curr_account, **data)

        return HttpResponse(f'{bookmark} bookmark object created')


    def put(self, request, *args, **kwargs):
        """
            Edits a bookmark from a bookmark table for the specific account
                    Parameters:
                        request.PUT has a form for data for the edited bookmark
                    Returns:
                        JSONRequest with success or error message
        """
        
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

        data = json.loads(request.body)
        result = Bookmark.objects.filter(pk = kwargs["id"]).update(**data)

        return HttpResponse(f'Bookmark object edited')

    def get(self, request, *args, **kwargs):
        """
        Gets a specific bookmark from a bookmark table for the specific account
                    Parameters:
                        request.GET has an id for a bookmark
                    Returns:
                        JSONRequest with success message and a bookmark or error message
        """
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

        bookmark = Bookmark.objects.filter(account = curr_account)
    
        data = BookmarkSerializer(bookmark, many=True)
        
        return JsonResponse(data.data, safe=False)

    def delete(self, request, *args, **kwargs):
        url = request.path.split('/')

        if not url[-1]:
            url = url[:-1]

        if url[-1] == 'all':
            return self.delete_all_bookmarks(request, *args, **kwargs)
        else:
            return self.delete_bookmark(request, *args, **kwargs)

    def delete_bookmark(self, request, *args, **kwargs):
        """
            Removes a bookmark from a bookmark table for the specific account
                    Parameters:
                        request.DELETE has an id for a bookmark
                    Returns:
                        JSONRequest with success or error message
        """
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

        bookmark = Bookmark.objects.filter(account = curr_account, pk = kwargs["id"]).delete()

        return HttpResponse(f'{bookmark} Bookmark object removed')

        

    def delete_all_bookmarks(self, request, *args, **kwargs):
        """
        Removes all bookmark from a bookmark table for the specific account
                    Parameters:
                        request.DELETE has an id for a bookmark
                    Returns:
                        JSONRequest with success or error message
        """
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

        bookmarks = Bookmark.objects.filter(account = curr_account).delete()

        return HttpResponse(f'{bookmarks} Bookmark object removed')