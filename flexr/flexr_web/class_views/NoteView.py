from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.validators import EMPTY_VALUES
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from ..serializers import NoteSerializer

import json
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

        # get requested note object and all accounts for user
        obj = curr_account.notes.get(pk=kwargs['pk'])
        accounts = curr_user.accounts.all()

        # get form object and initialize it with data
        form = EditNoteForm()
        form.fields['title'].initial = obj.title
        form.fields['content'].initial = obj.content

        # request messages for debugging
        if ('message' in self.request.session):
            message = self.request.session['message']
            del self.request.session['message']
            messages.success(self.request, message)
        elif ('err_message' in self.request.session):
            message = self.request.session['err_message']
            del self.request.session['err_message']
            messages.error(self.request, message)

        # get if note is locked
        locked = obj.lock

        # check that note is unlocked successfully
        if('note_unlocked' in self.request.session):
            id = self.request.session['note_unlocked']
            if( id == obj.id):
                locked = False
            del self.request.session['note_unlocked']

        # display note on the page
        return render(self.request, "flexr_web/note.html", 
        {"object": obj, 
         "form": form, 
         "accounts": accounts, 
         "locked": locked})

    def edit_note(self, request, *args, **kwargs):
        """
        Edit a note
        """

        # get form object on the page
        form = EditNoteForm(request.POST)
        #print("Note edited")

        # check if form is valid
        if form.is_valid():

            # get current account
            curr_acc = Account.objects.get(account_id = request.session['account_id'])
            
            # get information from form
            title = request.POST.get('title')
            content = request.POST.get('content')
            
            # get requested note and update with requested data
            obj = curr_acc.notes.get(pk=kwargs['pk'])
            obj.title = title
            obj.content = content
            obj.save()

        # request messages for debugging
            request.session['message'] = "Note edited"
        request.session['err_message'] = "Note could not be edited"

        # display requested note after editing 
        return redirect('/opennote/'+str(obj.id))

    def unlock_note(self, request, *args, **kwargs):
        """
        Unlock a note
        """

        # get current account
        current_acc = request.user.accounts.get(account_id = request.session['account_id'])

        # grab stored password and requested note
        form_password = request.POST.get('password')
        note = current_acc.notes.get(pk = kwargs['pk'])

        # check that password is correct
        # and setup request message for debugging
        if(note.password == form_password):
            request.session['note_unlocked'] = kwargs['pk']
            request.session['message'] = "Note unlocked"
        else:
            request.session['err_message'] = "Wrong password"

        # display requested note after unlock attempt
        return redirect('/opennote/' + str(kwargs['pk']))


@method_decorator(csrf_exempt, name='dispatch')
class NoteViewAPI(LoginRequiredMixin, DetailView):

    def post(self, request, *args, **kwargs):
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id=request.session['account_id'])

        data = json.loads(request.body)
        note = Note.objects.get_or_create(account=curr_account, url=data['url'])[0]
        data['note_id'] = note.id

        note = Note.objects.create(account=curr_account, **data)

        data = NoteSerializer(note)

        return JsonResponse(data.data, safe=False)

    def get(self, request, *args, **kwargs):
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id=request.session['account_id'])

        note = Note.objects.filter(account=curr_account)

        data = NoteSerializer(note, many=True)

        return JsonResponse(data.data, safe=False)