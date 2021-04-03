from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView
from django.http import HttpResponse, JsonResponse

import json
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
        # shared_folder.title = request.POST.get("new_title")
        # shared_folder.title = request.POST.get("new_description")
        form = EditSharedFolder(request.POST)
        if form.is_valid():
            shared_folder.title = request.POST.get("new_title")
            shared_folder.title = request.POST.get("new_description")
            print("\n\n\n\nit'svalid")
            shared_folder.title = request.POST.get('title')
            shared_folder.description = request.POST.get('description')
            tileo = form.cleaned_data['title']
            descrippy = form.cleaned_data['description']
            collaboratoros = form.cleaned_data['collaborators']
            bookmarkos = form.cleaned_data['bookmarks']
            tabos = form.cleaned_data['tabs']
            noteso = form.cleaned_data['notes']
            shared_folder.collaborators.set(collaboratoros)
            shared_folder.bookmarks.set(bookmarkos)
            shared_folder.notes.set(noteso)
            shared_folder.tabs.set(tabos)
        shared_folder.save()
        context = {'form': form}
        # return render('shared_folder/' + str(shared_folder.pk))
        return redirect('/shared_folder/' + str(shared_folder.id))

class FoldersViewAPI(LoginRequiredMixin, DetailView):

    def put(self, request, *args, **kwargs):
        """
            Edit
        """
        
        return HttpResponse()

    def post(self, request, *args, **kwargs):
        """
            Create
        """
        current_acc = request.user
        current_acc = current_acc.accounts.get(account_id = request.session['account_id'])
        data = json.loads(request.body)
        # data = folderSerializer(to be written and finalized)
        return HttpResponse()

    def get(self, request, *args, **kwargs):
        current_acc = request.user.accounts.get(account_id=request.session['account_id'])
        shared_folder = current_acc.shared_folders.get(id=kwargs['pk'])
        shared_folder = sharedFolder.objects.filter(owner = current_acc, description=shared_folder.description)
        return HttpResponse()

    def delete(self, request, *args, **kwargs):
        current_acc = request.user.accounts.get(account_id=request.session['account_id'])
        shared_folder = current_acc.shared_folders.get(id=kwargs['pk'])
        shared_folder = sharedFolder.objects.filter(owner = current_acc, description=shared_folder.description)
        return JsonResponse({"successful": "folder deleted"})
