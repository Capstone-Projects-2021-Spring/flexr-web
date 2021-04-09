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
        form = notef

        # request messages for debugging
        if ('message' in self.request.session):
            message = self.request.session['message']
            del self.request.session['message']
            messages.success(self.request, message)
        elif ('err_message' in self.request.session):
            message = self.request.session['err_message']
            del self.request.session['err_message']
            messages.error(self.request, message)
        request.session['prev_url'] = '/notes/'

        # display the page
        return render(self.request, "flexr_web/notes.html", 
        {"Notes": notes, 
        "Accounts": accounts, 
        'form': form})

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
                    print("reached",passw)
                    request.session['err_message'] = "Note not created. Please put a password on locked note"
                    return redirect(request.session['prev_url'])
                lo = False

            newnote = Note.objects.create(account=acc, title=tit, content=cont, lock=lo, password=passw)
            newnote.save()
            request.session['message'] = "Note created"

        else:
            request.session['err_message'] = "Note not created. Please put a password on locked note"
            #print(form.errors)

        return redirect(request.session['prev_url'])


    def delete_note(self,request, *args, **kwargs):
        """
        Delete a note
        """

        # grab requested note object
        obj = Note.objects.get(pk=kwargs['pk'])

        # delete note object
        obj.delete()

        # return to notes page
        if(request.session['prev_url'] != '/opennote/'+str(kwargs['pk'])+'/'):
            return redirect(request.session['prev_url'])
        else:
            print(request.session['prev_url'])
            return redirect('/notes/')
