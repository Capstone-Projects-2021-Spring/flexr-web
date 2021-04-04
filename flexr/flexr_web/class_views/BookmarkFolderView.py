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
from ..serializers import BookmarkSerializer, BookmarkFolderSerializer

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

        request.session['prev_url'] = '/bookmark_folder/'+str(kwargs['pk'])+'/'
        # Gerald: using redirect doesn't work here?
        return render(request, "flexr_web/bookmark_folder.html",
         {"Bookmarks": bookmarks, 
          "formb": formb,
          "bookmark_folder": bookmark_folder,
          "form": form})

    def get(self,request,  *args, **kwargs):
        """
        Display a single shared folder
        """
  
        # get the current account and requested shared folder
        current_acc = request.user.accounts.get(account_id = request.session['account_id'])
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
        request.session['prev_url'] = '/bookmark_folder/' + str(kwargs['pk'])
        # display the page
        return render(request, "flexr_web/bookmark_folder.html",
         {"bookmark_folder": bookmark_folder, 
          "formb": formb,
          "form": form,
          "Bookmarks": bookmarks})

    def create_bookmark_folder_web(self, request, *args, **kwargs):
    
        form = BookmarkFolderForm(request.POST)

        # check that the form is valid
        if form.is_valid():
            # form.save()
            #print(request.POST)

            # grab information from the form
            title = form.cleaned_data['title']
            owner = request.user.accounts.get(account_id = request.session['account_id'])
            bookmarks = form.cleaned_data['bookmarks']

            # create shared folder object and set its attributes
            folder = bookmarkFolder.objects.create(title = title, owner = owner)
            folder.bookmarks.set(bookmarks)
            folder.save()

        # request message for debugging
            request.session['message'] = "Bookmark Folder created"

        else:
            request.session['err_message'] = "Bookmark Folder not created."
            #print(form.errors)

        # return to shared folders page
        return redirect(request.session['prev_url'])
          
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
        return redirect(request.session['prev_url'])

    def delete_bookmark_folder_web(self, request, *args, **kwargs):
        current_acc = request.user.accounts.get(account_id = request.session['account_id'])
        obj = current_acc.bookmark_folders.get(id=kwargs['pk'])
            # delete note object
        obj.delete()

            # return to notes page
        return redirect('/bookmarks')

@method_decorator(csrf_exempt, name='dispatch')
class BookmarkFoldersViewAPI(LoginRequiredMixin, DetailView):

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

        # if 'url' in data:
        #     site = Site.objects.get_or_create(account = curr_account, url = data['url'])[0]
        #     data['site_id'] = site.id

        bookmark_folder = bookmarkFolder.objects.create(owner=curr_account, **data)

        data = BookmarkFolderSerializer(bookmark_folder)
        
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

        bookmark_folder = bookmarkFolder.objects.filter(owner = curr_account)
        data = BookmarkFolderSerializer(bookmark_folder, many=True)
        return JsonResponse(data.data, safe=False)

    def delete(self, request, *args, **kwargs):
        user = request.user
        account = user.accounts.get(account_id = request.session['account_id'])

        folder = bookmarkFolder.objects.filter(owner = account, pk = kwargs["id"]).delete()

        # folder = account.bookmark_folders.get(pk=kwargs['pk']).delete()
        # obj = account.bookmark_folders.get(id = kwargs['pk'])
            # delete note object
        # obj.delete()
        return JsonResponse({"successful": "folder deleted"})

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

        # if 'url' in data:
        #     site = Site.objects.get_or_create(account = curr_account, url = data['url'])[0]
        #     data['site_id'] = site.id

        result = bookmarkFolder.objects.filter(owner = curr_account, pk = kwargs["id"]).update(**data)

        # data = BookmarkFolderSerializer(result)
        
        return JsonResponse({"successful": "folder updated"})
