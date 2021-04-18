from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

import pytz

from ..models import *
from ..forms import *

# TODO: Gerald add request messages
# TODO: Gerald add comments

class SharedFoldersView(LoginRequiredMixin, View):
    """
    View class for the shared folders page
    """


    def get(self, request, *args, **kwargs):
        """
        Display the shared folders page
        """

        # get current user and current account
        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id = self.request.session['account_id'])

        # get all folders for the current account
        folders = curr_account.collab_shared_folders.all()

        # created a shared folder and populate its attributes
        folder_form = EditSharedFolder()
        friends = curr_account.friends.all()
        print("SharedFoldersView: get(): friends: ", friends)

        # request messages for debugging
        if ('message' in self.request.session):
            message = self.request.session['message']
            del self.request.session['message']
            messages.success(self.request, message)
        elif ('err_message' in self.request.session):
            message = self.request.session['err_message']
            del self.request.session['err_message']
            messages.error(self.request, message)
        request.session['prev_url'] = '/shared_folders/'
        # display the page
        return render(self.request, "flexr_web/shared_folders.html", 
        {"Folders": folders, 
         "folder_form": folder_form})

    
    def create_shared_folder(self, request, *args, **kwargs):
        """
        Create a shared folder
        """
        # Change required fields on the form.
    
        # get the form object
        form = EditSharedFolder(request.POST)

        # check that the form is valid
        if form.is_valid():
            # form.save()
            #print(request.POST)

            # grab information from the form
            title = form.cleaned_data['title']
            desc = form.cleaned_data['description']
            owner = request.user.accounts.get(account_id = request.session['account_id'])


            # create shared folder object and set its attributes
            folder = sharedFolder.objects.create(title = title, description = desc, owner = owner)
            folder.collaborators.add(owner)
            folder.save()

        # request message for debugging
            request.session['message'] = "Shared Folder created"

        else:
            request.session['err_message'] = "Shared Folder not created."
            #print(form.errors)

        # return to shared folders page
        return redirect(request.session['prev_url'])

    def delete_shared_folder(self,request, *args, **kwargs):
        print("SharedFoldersView: delete_shared_folder(): shared_folder", sharedFolder.objects.get(pk=kwargs['pk']))
        my = sharedFolder.objects.get(pk=kwargs['pk'])
        my.delete()
        return redirect('/shared_folders/')

    def edit_shared_folder(self, request, *args, **kwargs):
        form = EditSharedFolder(request.POST)
        if form.is_valid():
            print("SharedFoldersView: edit_shared_folder: Message: form is valid")

        return redirect(request.session['prev_url'])