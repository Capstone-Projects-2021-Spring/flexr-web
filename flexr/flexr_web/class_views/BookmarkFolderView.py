from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

import pytz

from ..models import *
from ..forms import *

# TODO: Gerald add request messages
# TODO: Gerald add comments

class BookmarkFolderView(LoginRequiredMixin, View):
    """
    View class for a single shared folder
    """

    def post(self, request, *args, **kwargs):
        """
        Filter the account's history by datetime range
        """

        # get current user and current account
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
        bookmark_folder = curr_account.bookmark_folders.get(id = kwargs['pk'])

        # get all user's accounts
        # accounts = curr_user.accounts.all()

        # get form object on page
        form = FilterBookmarkForm
        formb = BookmarkFolderForm

        owner = bookmark_folder.owner

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
        bookmarks = bookmark_folder.bookmarks.all()

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

        # Gerald: using redirect doesn't work here?
        return render(request, "flexr_web/bookmark_folder.html",
         {"Bookmarks": bookmarks, 
          "formb": formb,
          "bookmark_folder": bookmark_folder,
          "form": form})

    def get(self, *args, **kwargs):
        """
        Display a single shared folder
        """

        # get the current account and requested shared folder
        current_acc = self.request.user.accounts.get(account_id = self.request.session['account_id'])
        bookmark_folder = current_acc.bookmark_folders.get(id = kwargs['pk'])
        form = FilterBookmarkForm
        formb = EditBookmarkForm()
        formb.fields['bookmarks'].queryset = current_acc.bookmarks.all()
        # grab attributes for the shared folder
        owner = bookmark_folder.owner
        #CHANGE THIS TO NOT USE THE SHARED FOLDERS COLLABORATORS, this was written this way for testing the view method
        #print(collaborators)
        #print(tabs)
        bookmarks = bookmark_folder.bookmarks.all()

        # if a tab, bookmark, note is in the shared folder. Then the way we have the api's set up the user that doesn't own the object will now not be able to view, edit, or delete the object
        # we may want to add a field to each object that says "shared"

        # return render(request, "flexr_web/shared_folder.html", {"SharedFolder": shared_folder, "Collaborators": collaborators, "Tabs": tabs, "Bookmarks": bookmarks, "Notes": notes})

        # display the page
        return render(self.request, "flexr_web/bookmark_folder.html",
         {"bookmark_folder": bookmark_folder, 
          "formb": formb,
          "form": form,
          "Bookmarks": bookmarks})
          
    def edit_bookmark_folder(self, request, *args, **kwargs):
        current_acc = request.user.accounts.get(account_id=request.session['account_id'])
        bookmark_folder = current_acc.bookmark_folders.get(id=kwargs['pk'])
        """
        """

        form = EditBookmarkForm(request.POST)
        form.fields['bookmarks'].queryset = current_acc.bookmarks.all()
        # check if form is valid
        if form.is_valid():

            
            title = request.POST.get('title')

            bookmarkos = form.cleaned_data['bookmarks']

            bookmark_folder.title = title
            bookmark_folder.bookmarks.set(bookmarkos)


            request.session['message'] = "Bookmark edited"

        return redirect('/bookmark_folder/'+str(bookmark_folder.id))
