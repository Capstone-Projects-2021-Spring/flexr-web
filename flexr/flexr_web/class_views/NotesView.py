from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.validators import EMPTY_VALUES
from django.shortcuts import redirect, render
from django.views import View

import pytz

from ..models import *
from ..forms import *

# Gerald: why is notef in its own file?
from ..note_form import notef 

# TODO: Gerald more comments
class NotesView(LoginRequiredMixin, View):
    """
    View class for the notes page
    """

    def get(self,request, *args, **kwargs):
        """
        Display the notes page
        """
        # get current user and current account
        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id = self.request.session['account_id'])

        # get all user's accounts and notes
        accounts = curr_user.accounts.all()
        notes = curr_account.notes.all()

        # get note form object on the page
        form = CreateNoteForm
        fform = FilterNoteForm

        # request messages for debugging
        if ('message' in self.request.session):
            message = self.request.session['message']
            del self.request.session['message']
            messages.success(self.request, message)
        elif ('err_message' in self.request.session):
            message = self.request.session['err_message']
            del self.request.session['err_message']
            messages.error(self.request, message)
        request.session['redirect_url'] = '/notes/'

        # display the page
        return render(self.request, "flexr_web/notes.html", 
        {"Notes": notes, 
        "Accounts": accounts, 
        'form': form,
        "searched":False,
        'fform': fform})


    def post(self, request, *args, **kwargs):
        """
        Filter the account's history by datetime range
        """

        curr_user = request.user
        curr_acc = curr_user.accounts.get(account_id = request.session['account_id'])
        notes = curr_acc.notes.all()

        
        search = request.POST.get('search')
        print("NotesView: search_note: search: ", search)
        content_search = notes.filter(content__icontains=search)
        title_search = notes.filter(title__icontains = search)

        search_results = content_search | title_search
        search_results = search_results.distinct()
        print("NotesView: search_note: search_results: ", search_results)
        form = notef
        fform = FilterNoteForm
        if(search_results.count() > 0): 
            request.session['message'] = "Notes filtered"
        else:
            request.session['err_message'] = "No notes found"

        # request messages for debugging
        if ('message' in request.session):
            message = request.session['message']
            del request.session['message']
            messages.success(request, message)
        elif ('err_message' in request.session):
            message = request.session['err_message']
            del request.session['err_message']
            messages.error(request, message)
        request.session['redirect_url'] = '/notes/'

        # request message for debugging
        # request.session['message'] = "History Filtered"
        return render(self.request, "flexr_web/notes.html", 
        {"Notes": search_results, 
        'form': form,
        'searched':True,
        'fform': fform})

    def create_note(self, request, *args, **kwargs):
        """
        Create a new note
        """

        # get form object 
        form = notef(request.POST)

        # check that form is valid
        if form.is_valid():

            # get current account
            acc = request.user.accounts.get(account_id = request.session['account_id'])

            # grab note information from the form 
            tit = request.POST.get('title')
            cont = request.POST.get('content')
            lo = request.POST.get('lock')
            passw = request.POST.get('password')

            # check whether note is password locked
            if lo == 'on':
                lo = True

            else:
                if (passw not in EMPTY_VALUES):
                    request.session['err_message'] = "Note not created. Please put a password on locked note"
                    return redirect(request.session['redirect_url'])
                lo = False

            newnote = Note.objects.create(account=acc, title=tit, content=cont, lock=lo, password=passw)
            newnote.save()
            request.session['message'] = "Note created"

        else:
            request.session['err_message'] = "Note not created. Please put a password on locked note"

        return redirect(request.session['redirect_url'])


    def delete_note(self,request, *args, **kwargs):
        """
        Delete a note
        """

        # grab requested note object
        obj = Note.objects.get(pk=kwargs['pk'])

        # delete note object
        obj.delete()

        # return to notes page
        if(request.session['redirect_url'] != '/opennote/'+str(kwargs['pk'])+'/'):
            return redirect(request.session['redirect_url'])
        else:
            return redirect('/notes/')

    def search_note(self, request):
        curr_user = request.user
        curr_acc = curr_user.accounts.get(account_id = request.session['account_id'])
        notes = curr_acc.notes.all()

        
        search = request.POST.get('search')
        print("NotesView: search_note: search: ", search)
        content_search = notes.filter(content__icontains=search)
        title_search = notes.filter(title__icontains = search)

        search_results = content_search | title_search
        search_results = search_results.distinct()
        print("NotesView: search_note: search_results: ", search_results)
        form = notef
        fform = FilterNoteForm
        if(search_results.count() > 0): 
            request.session['message'] = "Notes filtered"
        else:
            request.session['err_message'] = "No notes found"

        # request messages for debugging
        if ('message' in request.session):
            message = request.session['message']
            del request.session['message']
            messages.success(request, message)
        elif ('err_message' in request.session):
            message = request.session['err_message']
            del request.session['err_message']
            messages.error(request, message)
        request.session['redirect_url'] = '/notes/'

        # display the page
        return render(request, "flexr_web/notes.html", 
        {"Notes": search_results, 
        'form': form,
        'fform': fform})