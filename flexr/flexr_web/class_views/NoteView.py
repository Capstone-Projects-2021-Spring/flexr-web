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

    def get(self,request,  *args, **kwargs):
        """
        Display a single note
        """
        # get current user and current account
        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id=self.request.session['account_id'])

        # get requested note object and all accounts for user
        obj = Note.objects.get(pk=kwargs['pk'])
        accounts = curr_user.accounts.all()

        # get form object and initialize it with data
        form = EditNoteForm()
        form.fields['title'].initial = obj.title
        form.fields['title'].label = ""
        form.fields['content'].initial = obj.content
        form.fields['content'].label = ""
        form.fields['lock'].label = "Lock:"
        form.fields['lock'].initial = obj.lock
        form.fields['password'].label = "Password:"
        form.fields['password'].initial = obj.password

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

        request.session['redirect_url'] = '/opennote/'+ str(kwargs['pk'])+'/'
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
        # check if form is valid
        if form.is_valid():
            
            # get current account
            acc = request.user.accounts.get(account_id = request.session['account_id'])
            noteid = kwargs['pk']
            note = acc.notes.get(id = noteid)
            print("NotesView: edit_note(): note: ", note)
            # grab note information from the form 
            tit = request.POST.get('title')
            cont = request.POST.get('content')
            lo = request.POST.get('lock')
            print("NotesView: edit_note(): locked: ", lo)
            passw = request.POST.get('password')
            passw2 = request.POST.get('password2')
            if passw != note.password and passw != passw2:
                request.session['note_unlocked'] = noteid
                request.session['err_message'] = "Note not edited. Passwords do not match"
                return redirect(request.session['redirect_url'])

            # check whether note is password locked
            if lo == 'on':
                lo = True
            else:
                if (passw not in EMPTY_VALUES):
                    request.session['note_unlocked'] = noteid
                    request.session['err_message'] = "Note not edited. Please put a password on locked note"
                    return redirect(request.session['redirect_url'])
                lo = False

            note.title = tit
            note.content = cont
            note.locked = lo
            note.password = passw
            note.save()
            request.session['note_unlocked'] = noteid
            request.session['message'] = "Note edited"

        else:
            request.session['note_unlocked'] = kwargs['pk']
            request.session['err_message'] = "Note not edited. Please put a password on locked note"

        return redirect(request.session['redirect_url'])

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
        return redirect(request.session['redirect_url'])


@method_decorator(csrf_exempt, name='dispatch')
class NoteViewAPI(LoginRequiredMixin, DetailView):

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id=request.session['account_id'])
        data = json.loads(request.body)
        # TODO: make this work
        note = Note.objects.create(account=curr_account, **data)
        data = NoteSerializer(note)
        return JsonResponse(data.data, safe=False)

    def get_all(self, request):
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id=request.session['account_id'])
        notes = curr_account.notes.all()
        data = NoteSerializer(notes, many=True)
        return JsonResponse(data.data, safe=False)

    def get(self, request, *args, **kwargs):
        url = request.path.split('/')

        if url[-2] == 'notes':
            return self.get_all(request, *args, **kwargs)
        else:
            return self.get_note(request, *args, **kwargs)

    def get_note(self, request, *args, **kwargs):
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id=request.session['account_id'])
        note = curr_account.notes.get(id = kwargs['id'])
        data = NoteSerializer(note, many=False)
        return JsonResponse(data.data, safe=False)

    @method_decorator(csrf_exempt)
    def put(self, request, *args, **kwargs):
        curr_user = request.user
        curr_acc = curr_user.accounts.get(account_id=request.session['account_id'])

        # TODO: make this access and update properly
        note = curr_acc.notes.get(pk=kwargs['id'])
        request_data = json.loads(request.body)
        note.title = request_data['title']
        note.content = request_data['content']
        note.lock = request_data['lock']
        note.password = request_data['password']
        note.save()
        data = NoteSerializer(note)
        return JsonResponse(data.data, safe=False)

    def delete(self, request, *args, **kwargs):
        curr_user = request.user
        curr_acc = curr_user.accounts.get(account_id=request.session['account_id'])
        note = curr_acc.notes.get(pk=kwargs['id']).delete()
        return JsonResponse({"success": "bookmark deleted"})


