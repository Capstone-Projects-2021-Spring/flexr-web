from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

import pytz

from ..models import *
from ..forms import *

# TODO: Gerald add request messages
# TODO: Gerald add comments

class SharedFolderView(LoginRequiredMixin, View):
    """
    View class for a single shared folder
    """

    def get(self, *args, **kwargs):
        """
        Display a single shared folder
        """

        # get the current account and requested shared folder
        current_acc = self.request.user.accounts.get(account_id = self.request.session['account_id'])
        shared_folder = current_acc.shared_folders.get(id = kwargs['pk'])

        # grab attributes for the shared folder
        owner = shared_folder.owner
        #CHANGE THIS TO NOT USE THE SHARED FOLDERS COLLABORATORS, this was written this way for testing the view method
        collaborators = shared_folder.collaborators.all()
        #print(collaborators)
        tabs = shared_folder.tabs.all()
        #print(tabs)
        bookmarks = shared_folder.bookmarks.all()
        notes = shared_folder.notes.all()

        # if a tab, bookmark, note is in the shared folder. Then the way we have the api's set up the user that doesn't own the object will now not be able to view, edit, or delete the object
        # we may want to add a field to each object that says "shared"

        # return render(request, "flexr_web/shared_folder.html", {"SharedFolder": shared_folder, "Collaborators": collaborators, "Tabs": tabs, "Bookmarks": bookmarks, "Notes": notes})

        # display the page
        return render(self.request, "flexr_web/shared_folder.html",
         {"shared_folder": shared_folder, 
          "Collaborators": collaborators, 
          "Tabs":tabs, 
          "Bookmarks": bookmarks, 
          "Notes": notes})