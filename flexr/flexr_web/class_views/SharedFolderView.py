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
        
        if (sharedFolder.objects.filter(id=kwargs['pk']).count() == 0):
            request.session['err_message'] = "Folder does not exist"
            return redirect('/shared_folders/')
        if (current_acc.collab_shared_folders.filter(id = kwargs['pk']).count() == 0):
            request.session['err_message'] = "You are not a collaborator on that shared folder"
            return redirect('/shared_folders/')
          
        shared_folder = current_acc.collab_shared_folders.get(id = kwargs['pk'])

        # grab attributes for the shared folder
        owner = shared_folder.owner
        
        collaborators = shared_folder.collaborators.all()
        #print(collaborators)
        tabs = shared_folder.tabs.all()
        #print(tabs)
        bookmarks = shared_folder.bookmarks.all()
        notes = shared_folder.notes.all()

        for x in notes:
            request.session['note_'+str(x.id)] = []
            for j in collaborators:
                request.session['note_'+str(x.id)].append(j.account_id)

        # Edit shared folder form
        form = EditSharedFolder()
        form.fields["title"].initial = shared_folder.title
        form.fields["description"].initial = shared_folder.description
        friends = current_acc.friends.all() 
        collabs = shared_folder.collaborators.all()
        print("SharedFolderView: get(): friends", friends)
        print("SharedFolderView: get(): collabs", collabs)
        # Collab_set is the set of collaborators
        collab_set = friends | collabs # this is how we merge two querysets
        collab_set = collab_set.distinct()

        # if a tab, bookmark, note is in the shared folder. Then the way we have the api's set up the user that doesn't own the object will now not be able to view, edit, or delete the object
        # we may want to add a field to each object that says "shared"

        # return render(request, "flexr_web/shared_folder.html", {"SharedFolder": shared_folder, "Collaborators": collaborators, "Tabs": tabs, "Bookmarks": bookmarks, "Notes": notes})
        friends_not_collab = current_acc.friends.exclude(account_id__in = collabs)

        request.session['redirect_url'] = '/shared_folder/'+str(kwargs['pk'])+'/' #set session key for redirect

        # request messages for debugging
        if ('message' in self.request.session):
            message = self.request.session['message']
            del self.request.session['message']
            messages.success(self.request, message)
        elif ('err_message' in self.request.session):
            message = self.request.session['err_message']
            del self.request.session['err_message']
            messages.error(self.request, message)

        myNotes = current_acc.notes.exclude(id__in = notes)
        myTabs = current_acc.tabs.exclude(id__in = tabs)
        myBookmarks =current_acc.bookmarks.exclude(id__in = bookmarks)

        # display the page
        return render(self.request, "flexr_web/shared_folder.html",
         {"shared_folder": shared_folder,
         'MyNotes':myNotes,
         "MyBookmarks": myBookmarks,
         "MyTabs": myTabs,
          "Collaborators": collaborators, 
          "Friends":friends_not_collab,
          "Tabs":tabs, 
          "Bookmarks": bookmarks, 
          "Notes": notes,
          "form": form})

    def edit_shared_folder(self, request, *args, **kwargs):
        current_acc = request.user.accounts.get(account_id=request.session['account_id'])
        shared_folder = current_acc.shared_folders.get(id=kwargs['pk'])
        # shared_folder.title = request.POST.get("new_title")
        # shared_folder.title = request.POST.get("new_description")
        form = EditSharedFolder(request.POST)
        # Process form for editing shared folder
        if form.is_valid():
            shared_folder.title = request.POST.get("new_title")
            shared_folder.title = request.POST.get("new_description")
            shared_folder.title = request.POST.get('title')
            shared_folder.description = request.POST.get('description')
            tileo = form.cleaned_data['title']
            descrippy = form.cleaned_data['description']

        shared_folder.save()
        context = {'form': form}
        # return render('shared_folder/' + str(shared_folder.pk))
        return redirect(request.session['redirect_url'])
        # return render(request, "flexr_web/shared_folder.html",
        #  {"shared_folder": obj,
        #   "Collaborators": collaborators,
        #   "Tabs":tabs,
        #   "Bookmarks": bookmarks,
        #   "Notes": notes},
        #   "form: form")

    def add_collaborator(self, request, *args, **kwargs):
        user_account = request.user.accounts.get(account_id=request.session['account_id'])
        collab_id = request.POST.get('search_id')
        shared_folder = sharedFolder.objects.get(id = kwargs['id'])
        print("SharedFolderView: add_collaborator(): collab_id: ", collab_id)
        collab_acc_username = request.POST.get('search_username')
        print("SharedFolderView: add_collaborator(): collab_acc_username: ", collab_acc_username)
        try:
            collab_account = Account.objects.get(account_id=collab_id, username = collab_acc_username)
            shared_folder.collaborators.add(collab_account)
            request.session['message'] = "User added as collaborator"
            return redirect(request.session['redirect_url'])
        except:
            request.session['err_message'] = "User could not be added as collaborator"
            return redirect(request.session['redirect_url'])

    def remove_collaborator(self, request, *args, **kwargs):
        user_account = request.user.accounts.get(account_id=request.session['account_id'])
        collab_id = request.POST.get('search_id')
        if(user_account.shared_folders.filter(id = kwargs['id']).count() == 0):
            request.session['err_message'] = "Shared folder does not exist"
            return redirect(request.session['redirect_url'])

        shared_folder = sharedFolder.objects.get(id = kwargs['id'])
        print("SharedFolderView: remove_collaborator(): collab_id: ", collab_id)
        collab_acc_username = request.POST.get('search_username')
        print("SharedFolderView: remove_collaborator(): collab_acc_username: ", collab_acc_username)
        try:
            collab_account = Account.objects.get(account_id=collab_id, username = collab_acc_username)
            shared_folder.collaborators.remove(collab_account)
            if(collab_account == shared_folder.owner):
                if(shared_folder.collaborators.all().count() > 0):
                    shared_folder.owner = shared_folder.collaborators.all()[0]
                    shared_folder.save()
                    request.session['message'] = "User removed as collaborator and ownership was transferred"
                    return redirect(request.session['redirect_url'])
                else:
                    request.session['message'] = "Shared folder deleted."
                    shared_folder.delete()
                    return redirect('/shared_folders/')
            else:
                request.session['message'] = "User removed as collaborator"
                return redirect(request.session['redirect_url'])
        except:
            request.session['err_message'] = "User could not be removed as collaborator"
            return redirect(request.session['redirect_url'])

    def add_note(self, request, *args, **kwargs):
        user_account = request.user.accounts.get(account_id=request.session['account_id'])
        note_id = request.POST.get('note_id')
        shared_folder = sharedFolder.objects.get(id = kwargs['id'])
        # Some version if this error checking needs to be implemented at some point:
        # if (Note.objects.filter(id=kwargs['id']).count() == 0): 
        #     request.session['err_message'] = "Note does not exist"
        #     return redirect(request.session['redirect_url'])

        note = Note.objects.get(id = note_id)
        shared_folder.notes.add(note)
        request.session['message'] = "Note added!"
        return redirect(request.session['redirect_url'])

    def remove_note(self, request, *args, **kwargs):
        user_account = request.user.accounts.get(account_id=request.session['account_id'])
        note_id = request.POST.get('note_id')
        shared_folder = sharedFolder.objects.get(id = kwargs['id'])
        if (Note.objects.filter(id=kwargs['id']).count() == 0):
            request.session['err_message'] = "Note does not exist"
            return redirect(request.session['redirect_url'])
        
        note = Note.objects.get(id = note_id)
        shared_folder.notes.remove(note)
        request.session['message'] = "Note removed!"
        return redirect(request.session['redirect_url'])

    def add_tab(self, request, *args, **kwargs):
        user_account = request.user.accounts.get(account_id=request.session['account_id'])
        tab_id = request.POST.get('tab_id')
        shared_folder = sharedFolder.objects.get(id = kwargs['id'])
        
        # if (Tab.objects.filter(id=kwargs['id']).count() == 0):
        #     request.session['err_message'] = "Tab does not exist"
        #     return redirect(request.session['redirect_url'])
        tab = Tab.objects.get(id = tab_id)
        shared_folder.tabs.add(tab)
        request.session['message'] = "Tab added!"
        return redirect(request.session['redirect_url'])

    def remove_tab(self, request, *args, **kwargs):
        user_account = request.user.accounts.get(account_id=request.session['account_id'])
        tab_id = request.POST.get('tab_id')
        shared_folder = sharedFolder.objects.get(id = kwargs['id'])
        # if (Tab.objects.filter(id=kwargs['id']).count() == 0):
        #     request.session['err_message'] = "Tab does not exist"
        #     return redirect(request.session['redirect_url'])
        tab = Tab.objects.get(id = tab_id)
        shared_folder.tabs.remove(tab)
        request.session['message'] = "Tab removed!"
        return redirect(request.session['redirect_url'])

    def add_bookmark(self, request, *args, **kwargs):
        user_account = request.user.accounts.get(account_id=request.session['account_id'])
        bm_id = request.POST.get('bm_id')
        shared_folder = sharedFolder.objects.get(id = kwargs['id'])
        bm = Bookmark.objects.get(id = bm_id)
        # if (Bookmark.objects.filter(id=kwargs['id']).count() == 0):
        #     request.session['err_message'] = "Bookmark does not exist"
        #     return redirect('/shared_folders/')
        shared_folder.bookmarks.add(bm)
        request.session['message'] = "Bookmark added!"
        return redirect(request.session['redirect_url'])

    def remove_bookmark(self, request, *args, **kwargs):
        user_account = request.user.accounts.get(account_id=request.session['account_id'])
        bm_id = request.POST.get('bm_id')
        shared_folder = sharedFolder.objects.get(id = kwargs['id'])
        # if (Bookmark.objects.filter(id=kwargs['id']).count() == 0):
        #     request.session['err_message'] = "Bookmark does not exist"
        #     return redirect('/shared_folders/')
        bm = Bookmark.objects.get(id = bm_id)
        shared_folder.bookmarks.remove(bm)
        request.session['message'] = "Bookmark removed!"
        return redirect(request.session['redirect_url'])

@method_decorator(csrf_exempt, name='dispatch')
class FoldersViewAPI(LoginRequiredMixin, DetailView):

    def put(self, request, *args, **kwargs):
        """
            Edit
        """
        usero = request.user
        accounto = usero.accounts.get(account_id = request.session['account_id'])
        data = json.loads(request.body)
        shared_folder = sharedFolder.objects.get(pk = kwargs["id"])
        shared_folder.title = data['title']
        shared_folder.description = data['description']
        # TODO need to have this be a many to many field
        collaborators = data['collaborators']
        shared_folder.collaborators.clear()
        for acc in collaborators:
            account = Account.objects.get(account_id = acc['account_id'])
            shared_folder.collaborators.add(account)
    
        bookmarks = data['bookmarks']
        shared_folder.bookmarks.clear()
        for bm in bookmarks:
            bm_id = bm['id']
            bkmk = Bookmark.objects.get(id = bm_id)
            shared_folder.bookmarks.add(bkmk)

        tabs = data['tabs']
        shared_folder.tabs.clear()
        for tb in tabs:
            tb_id = tb['id']
            tab = Tab.objects.get(id = tb_id)
            shared_folder.tabs.add(tab)

        notes = data['notes']
        shared_folder.notes.clear()
        for nt in notes:
            nt_id = nt['id']
            note = Note.objects.get(id = nt_id)
            shared_folder.notes.add(note)
        shared_folder.save()
        data = SharedFolderSerializer(shared_folder)
        return JsonResponse(data.data, safe=False)

    def post(self, request, *args, **kwargs):
        """
            Create
        """
        usero = request.user
        accounto = usero.accounts.get(account_id = request.session['account_id'])
        shared_folder = sharedFolder.objects.create(owner = accounto)
        data = json.loads(request.body)
        shared_folder.title = data['title']
        shared_folder.description = data['description']
        shared_folder.created_date = data['created_date']
        shared_folder.owner = Account.objects.get(account_id = request.session['account_id'])
        # TODO need to have this be a many to many field
        collaborators = data['collaborators']
        for acc in collaborators:
            account = Account.objects.get(account_id = acc['account_id'])
            shared_folder.collaborators.add(account)
            
        shared_folder.collaborators.add(accounto)
        shared_folder.save()
        data = SharedFolderSerializer(shared_folder)
        return JsonResponse(data.data, safe=False)

    def get(self, request, *args, **kwargs):
        usero = request.user
        accounto = usero.accounts.get(account_id = request.session['account_id'])
        foldos = accounto.collab_shared_folders.all()
        data = SharedFolderSerializer(foldos, many=True)
        return JsonResponse(data.data, safe=False)

    def delete(self, request, *args, **kwargs):
        usero = request.user
        accounto = usero.accounts.get(account_id = request.session['account_id'])
        foldo = sharedFolder.objects.filter(pk = kwargs["id"]).delete()
        return JsonResponse({"successful": "folder deleted"})
