from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.validators import EMPTY_VALUES
from django.shortcuts import redirect, render
from django.views import View

import pytz

from ..models import *
from ..forms import *

# TODO: Gerald more comments
class NoteView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        """
        Display a single note
        """

        # get current user and current account
        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id=self.request.session['account_id'])

        obj = curr_account.notes.get(pk=kwargs['pk'])
        accounts = curr_user.accounts.all()


        form = EditNoteForm()
        form.fields['title'].initial = obj.title
        form.fields['content'].initial = obj.content

        if ('message' in self.request.session):
            message = self.request.session['message']
            del self.request.session['message']
            messages.success(self.request, message)
        elif ('err_message' in self.request.session):
            message = self.request.session['err_message']
            del self.request.session['err_message']
            messages.error(self.request, message)

        locked = obj.lock
        if('note_unlocked' in self.request.session):
            id = self.request.session['note_unlocked']
            if( id == obj.id):
                locked = False
            del self.request.session['note_unlocked']

        return render(self.request, "flexr_web/note.html", 
        {"object": obj, 
         "form": form, 
         "accounts": accounts, 
         "locked": locked})

    def edit_note(self, request, *args, **kwargs):
        """
        Edit a note
        """

        form = EditNoteForm(request.POST)
        print("Note edited")

        if form.is_valid():
            title = request.POST.get('title')
            content = request.POST.get('content')
            curr_acc = Account.objects.get(account_id = request.session['account_id'])
            obj = curr_acc.notes.get(pk=kwargs['pk'])
            obj.title = title
            obj.content = content
            obj.save()
            request.session['message'] = "Note edited"
        request.session['err_message'] = "Note could not be edited"

        return redirect('/opennote/'+str(obj.id))

    def unlock_note(self, request, *args, **kwargs):

        current_acc = request.user.accounts.get(account_id = request.session['account_id'])
        form_password = request.POST.get('password')
        note = current_acc.notes.get(pk = kwargs['pk'])

        if(note.password == form_password):
            request.session['note_unlocked'] = kwargs['pk']
            request.session['message'] = "Note unlocked"
        else:
            request.session['err_message'] = "Wrong password"

        return redirect('/opennote/' + str(kwargs['pk']))