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

        form = EditSharedFolder()
        form.fields["title"].initial = shared_folder.title
        form.fields["description"].initial = shared_folder.description
        form.fields["collaborators"].initial = shared_folder.collaborators.all()
        form.fields["bookmarks"].initial = shared_folder.bookmarks.all()
        form.fields["tabs"].initial = shared_folder.tabs.all()
        form.fields["notes"].initial = shared_folder.notes.all()

        # if a tab, bookmark, note is in the shared folder. Then the way we have the api's set up the user that doesn't own the object will now not be able to view, edit, or delete the object
        # we may want to add a field to each object that says "shared"

        # return render(request, "flexr_web/shared_folder.html", {"SharedFolder": shared_folder, "Collaborators": collaborators, "Tabs": tabs, "Bookmarks": bookmarks, "Notes": notes})

        # display the page
        return render(self.request, "flexr_web/shared_folder.html",
         {"shared_folder": shared_folder,
          "Collaborators": collaborators, 
          "Tabs":tabs, 
          "Bookmarks": bookmarks, 
          "Notes": notes,
          "form": form})

    def edit_shared_folder(self, request, *args, **kwargs):
        current_acc = request.user.accounts.get(account_id=request.session['account_id'])
        shared_folder = current_acc.shared_folders.get(id=kwargs['pk'])
        print(request.POST.get("new_title"))
        shared_folder.title = request.POST.get("new_title")
        shared_folder.title = request.POST.get("new_description")
        # form = EditSharedFolder(request.POST)
        #
        # collaborators = obj.collaborators.all()
        # tabs = obj.tabs.all()
        # bookmarks = obj.bookmarks.all()
        # notes = obj.notes.all()
        form = EditSharedFolder(request.POST)
        if form.is_valid():
            print("\n\n\n\nit'svalid")
            shared_folder.title = request.POST.get('title')

        shared_folder.save()
        context = {'form': form}
        # return render('shared_folder/' + str(shared_folder.pk))
        return redirect('/shared_folder/' + str(shared_folder.id))
        # return render(request, "flexr_web/shared_folder.html",
        #  {"shared_folder": obj,
        #   "Collaborators": collaborators,
        #   "Tabs":tabs,
        #   "Bookmarks": bookmarks,
        #   "Notes": notes},
        #   "form: form")

    # def edit_shared_folder(self, request, *args, **kwargs):
    #     """
    #     Edit a note
    #     """
    #
    #     # get form object on the page
    #     form = EditSharedFolder(request.POST)
    #     # print("Note edited")
    #     obj = Account.objects.get(account_id=request.session['account_id']).shared_folders.get(pk=kwargs['pk'])
    #     # check if form is valid
    #     if form.is_valid():
    #         # get current account
    #         curr_acc = Account.objects.get(account_id=request.session['account_id'])
    #
    #         # get information from form
    #         title = request.POST.get('title')
    #         # content = request.POST.get('content')
    #
    #         # get requested note and update with requested data
    #         obj = curr_acc.shared_folders.get(pk=kwargs['pk'])
    #         obj.title = title
    #         obj.content = content
    #         obj.save()
    #
    #         # request messages for debugging
    #         request.session['message'] = "Note edited"
    #     request.session['err_message'] = "Note could not be edited"
    #
    #     # display requested note after editing
    #     return redirect('/opennote/' + str(obj.id))