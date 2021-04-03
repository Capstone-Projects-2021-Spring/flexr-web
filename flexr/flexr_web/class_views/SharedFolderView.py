from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import json
import pytz

from ..models import *
from ..forms import *
from ..serializers import SharedFolderSerializer

# TODO: Gerald add request messages
# TODO: Gerald add comments

class SharedFolderView(LoginRequiredMixin, View):
    """
    View class for a single shared folder
    """

    def get(self,request, *args, **kwargs):
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

        request.session['prev_url'] = '/shared_folder/'+str(kwargs['pk'])+'/'
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
        return redirect(request.session['prev_url'])
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

@method_decorator(csrf_exempt, name='dispatch')
class FoldersViewAPI(LoginRequiredMixin, DetailView):

    def put(self, request, *args, **kwargs):
        """
            Edit
        """
        usero = request.user
        accounto = usero.accounts.get(account_id = request.session['account_id'])
        data = json.loads(request.body)
        sharedFolder.objects.filter(pk = kwargs["id"]).update(**data)
        data = SharedFolderSerializer(shared_folder)
        return JsonResponse(data.data, safe=False)

    def post(self, request, *args, **kwargs):
        """
            Create
        """
        usero = request.user
        accounto = usero.accounts.get(account_id = request.session['account_id'])
        data = json.loads(request.body)
        # data = folderSerializer(to be written and finalized)
        foldo = sharedFolder.objects.create(**data, owner=accounto)
        return JsonResponse(data.data, safe=False)

    def get(self, request, *args, **kwargs):
        usero = request.user
        accounto = usero.accounts.get(account_id = request.session['account_id'])
        foldos = sharedFolder.objects.filter(owner=accounto)
        data = SharedFolderSerializer(foldos, many=True)
        return JsonResponse(data.data, safe=False)

    def delete(self, request, *args, **kwargs):
        usero = request.user
        accounto = usero.accounts.get(account_id = request.session['account_id'])
        foldo = sharedFolder.objects.filter(pk = kwargs["id"]).delete()
        return JsonResponse({"successful": "folder deleted"})
