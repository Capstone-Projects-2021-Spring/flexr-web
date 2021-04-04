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
    
    def post(self, request, *args, **kwargs):
        """
        Filter the account's history by datetime range
        """

        # get current user and current account
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

        # get all user's accounts
        # accounts = curr_user.accounts.all()

        # get form object on page
        form = FilterBookmarkForm
        formb = BookmarkFolderForm
        folders = curr_account.bookmark_folders.all()
        formf = BookmarkOnFile


        # grab date and time information from POST form
        # site = request.POST['site']
        start_date = request.POST['start_date']
        start_time = request.POST['start_time']
        end_date = request.POST['end_date']
        end_time = request.POST['end_time']

        # set default time if None
        if not start_time:
            start_time = '00:00'

        # set default time if None
        if not end_time:
            end_time = '00:00'

        # concat to datetime format
        start_datetime = start_date + ' ' + start_time
        end_datetime = end_date + ' ' + end_time

        # TODO: Gerald check that timezone's work correctly
        
        # grab all history objects
        bookmarks = curr_account.bookmarks.all()

        # filter based on site if given
        # if site:
        #     history = history.filter(site__url__icontains=site)

        # filter based on start if given
        if start_date:
            start = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M').replace(tzinfo = pytz.UTC)
            bookmarks = bookmarks.filter(
            created_date__gte=start)

        # filter based on end if given
        if end_date:
            end = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M').replace(tzinfo = pytz.UTC)
            bookmarks = bookmarks.filter(
            created_date__lte=end
        )

        # request message for debugging
        request.session['message'] = "Bookmark Filtered"

        request.session['prev_url'] = '/bookmarks/'
        # Gerald: using redirect doesn't work here?
        return render(request, "flexr_web/bookmarks.html",
         {"Bookmarks": bookmarks, 
          "formb": formb,
          "formf": formf,
          "Folders": folders,
          "form": form})


    def get(self,request, *args, **kwargs):
        """
        Display the bookmarks page
        """

        # get current user and current account
        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id = self.request.session['account_id'])

        # get all bookmarks for current user
        bookmarks = curr_account.bookmarks.all()
        form = FilterBookmarkForm
        formb = BookmarkFolderForm()
        formb.fields['bookmarks'].queryset = curr_account.bookmarks.all()
        folders = curr_account.bookmark_folders.all()
        formf = BookmarkOnFile
        # request messages for debugging
        if ('message' in self.request.session):
            message = self.request.session['message']
            del self.request.session['message']
            messages.success(self.request, message)

        elif ('err_message' in self.request.session):
            message = self.request.session['err_message']
            del self.request.session['err_message']
            messages.error(self.request, message)

        request.session['prev_url'] = '/bookmarks/'
        # display the page
        return render(self.request, "flexr_web/bookmarks.html", 
        {"Bookmarks": bookmarks,
        "formb": formb,
        "formf": formf,
        "Folders": folders,
        "form": form})


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
        bm_id = Bookmark.create_bookmark(tab, curr_account)
        site = tab.site
        site.bookmarked = bm_id
        site.save()
        tab.save()
        # request message for debugging
        request.session['message'] = "Bookmark Created"

        # go to open_tabs page
        return redirect(request.session['prev_url'])


    def delete_bookmark(self, request, *args, **kwargs):
        """
        Delete a bookmark from the current account
        """

        # get current user and current account
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
        bm = curr_account.bookmarks.get(id = kwargs['id'])
        site = bm.site
        site.bookmarked = 0
        site.save()
        # delete requested bookmark
        Bookmark.delete_bookmark(kwargs['id'])

        # request message for debugging
        request.session['message'] = "Bookmark Deleted"
        
        # return to bookmarks page
        return redirect(request.session['prev_url'])

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

        data = json.loads(request.body)

        if 'url' in data:
            site = Site.objects.get_or_create(account = curr_account, url = data['url'])[0]
            data['site_id'] = site.id

        bookmark = Bookmark.objects.create(account=curr_account, **data)

        data = BookmarkSerializer(bookmark)
        
        return JsonResponse(data.data, safe=False)


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

        if 'url' in data:
            site = Site.objects.get_or_create(account = curr_account, url = data['url'])[0]
            data['site_id'] = site.id

        result = Bookmark.objects.filter(pk = kwargs["id"]).update(**data)

        data = BookmarkSerializer(bookmark)
        
        return JsonResponse(data.data, safe=False)

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

        return JsonResponse({"success": "bookmark deleted"})

        

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

        return JsonResponse({"success": "all bookmarks deleted"})