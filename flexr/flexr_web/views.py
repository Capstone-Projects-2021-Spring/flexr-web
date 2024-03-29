from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from django.contrib import messages, auth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.validators import EMPTY_VALUES
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.core import serializers
from pydoc import *
import json
from django.views.generic import *
from django.http import QueryDict
from .forms import *
from .note_form import notef
from django.contrib.auth import authenticate, login
from django.views import View

from django.views.decorators.csrf import csrf_exempt
from .models import *
from .serializers import *
import pytz
from django.db.models import Q
from itertools import chain
# Create your views here.

################## Managing Website Pages ##################

class IndexView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        curr_user = self.request.user
        try:
            print("IndexView curr_user")
            curr_account = curr_user.accounts.get(account_id = self.request.session['account_id'])
            print("IndexView: Account Successfully Switched: "+ str(curr_account))
        except:
            curr_account = curr_user.accounts.all()[0]
            self.request.session['account_id'] = curr_account.account_id
            print("IndexView: Account initialized:" )

        accounts = curr_user.accounts.all()
        history = curr_account.history.all()
        sites = curr_account.sites.all()
        tabs = curr_account.tabs.all()
        bookmarks = curr_account.bookmarks.all()
        notes = curr_account.notes.all()
        folders = sharedFolder.objects.filter(collaborators = curr_account.account_id)
        print(folders)
        # suggested_sites = curr_account.suggested_sites()
        print(curr_user)
        if ('message' in self.request.session):
            message = self.request.session['message']
            del self.request.session['message']
            messages.success(self.request, message)
        elif('err_message' in self.request.session):
            message = self.request.session['err_message']
            del self.request.session['err_message']
            messages.error(self.request, message)
        print("reached")
        form = AccountForm
        return render(self.request, "flexr_web/index.html",
                      {"curr_acc": curr_account, "Accounts": accounts, "Sites": sites, "Tabs": tabs, "Notes": notes,
                       "History": history, "Bookmarks": bookmarks, "Folders":folders,
                       "form": form})

@csrf_exempt
def switch_account(request,*args, **kwargs):

    #TODO implement these request messages for every call to change something in database
    #This will be usefull for testing
    try:

        request.user.accounts.get(account_id = kwargs["id"])
        print("switching account....")
        request.session['message'] = "Account Switched"
        request.session['account_id'] = kwargs["id"]
    except:
        print("error switching account....")
        request.session['err_message'] = "Error switching account"
    return HttpResponseRedirect('/')

def login_web(request):
    return None

def signup_web(request):
    return None

def register_web(request):
    if request.method == 'POST':
        form = registrationform(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                new_account = Account.objects.create(user=user, email=user.email, username = user.username)
                new_account.save()
                request.session['account_id'] = new_account.account_id
                return redirect('/')
            else:
                form = registrationform
                context = {'form': form}
                return render(request, 'registration/register.html', context)
    else:
        form = registrationform
    context = {'form' : form}
    return render(request, 'registration/register.html', context)

@login_required
def add_account_web(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            print(username)
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            type_of_account = request.POST.get("type_of_account")

            new_account = Account.objects.create(user=request.user, email=email, username = username, phone_number = phone_number, type_of_account = type_of_account)
            new_account.save()
            request.session['account_id'] = new_account.account_id
            request.session['message'] = "Account Created"
            return redirect('/')

@login_required
def edit_account_web(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        print(form.errors)

        if form.is_valid():
            username = request.POST.get('username')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            type_of_account = request.POST.get("type_of_account")
            account = Account.objects.get(account_id = request.session['account_id'])
            print(account)
            account.username = username
            account.email=email
            account.phone_number = phone_number
            account.type_of_account = type_of_account
            account.save()
            # messages.add_message(request, , 'A serious error occurred.')
            #TODO make sure that we error check everything
            request.session['message'] = "Account Edited"
            return redirect('/profile')

@login_required
def profile_web(request):
    curr_user = request.user

    print(curr_user)
    curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
    print(curr_account)
    accounts = curr_user.accounts.all()
    acc_pref = curr_account.account_preferences
    # site = curr_account.sites.all()[0]
    # acc_pref.home_page = site

    # print(acc_pref)
    pref_form = PreferencesForm()
    if(curr_account.account_preferences.home_page is not None):
        pref_form.fields['home_page'].initial = curr_account.account_preferences.home_page
        print(pref_form.fields['home_page'])
    else:
        try:
            pref_form.fields['home_page'].initial = curr_account.sites.all()[0] #This isn't good for a first time user
        except:
            site = Site.objects.create(account = curr_account, url = "https://google.com")
            site.save()
            pref_form.fields['home_page'].initial = site

    pref_form.fields['home_page'].queryset = curr_account.sites.all() # have to be sure to only show that user's sites!
    pref_form.fields['sync_enabled'].initial = curr_account.account_preferences.sync_enabled
    pref_form.fields['searchable_profile'].initial = curr_account.account_preferences.searchable_profile
    pref_form.fields['cookies_enabled'].initial = curr_account.account_preferences.cookies_enabled
    pref_form.fields['popups_enabled'].initial = curr_account.account_preferences.popups_enabled
    pref_form.fields['is_dark_mode'].initial = curr_account.account_preferences.is_dark_mode

    account_form = AccountForm()
    account_form.fields['username'].initial = curr_account.username
    account_form.fields['email'].initial = curr_account.email
    account_form.fields['phone_number'].initial = curr_account.phone_number
    account_form.fields['type_of_account'].initial = curr_account.type_of_account
    print("hello")

    if ('message' in request.session):
        message = request.session['message']
        del request.session['message']
        messages.success(request, message)
    elif ('err_message' in request.session):
        message = request.session['err_message']
        del request.session['err_message']
        messages.error(request, message)

    friends = curr_account.all_friends.all()
    friend_requests = curr_account.to_friend.all().filter(status = "Pending")
    print("friend requests", friend_requests)
    pending_friends = curr_account.all_pending_friends.all()
    print(pending_friends)
    # all_accounts =  Account.objects.filter(~Q(account_id__in=[o.account_id for o in accounts])) #this needs to be filter on account preferences searchable
    all_accounts = accounts
    print(all_accounts)
    return render(request, "flexr_web/profile.html", {"curr_acc":curr_account, "Accounts": accounts,
                                                      "Preferences":acc_pref, "pref_form": pref_form,
                                                      "account_form": account_form, "Friends":friends, "AllAccounts": all_accounts,
                                                      "friend_requests": friend_requests})

CHECKBOX_MAPPING = {'on':True,
                    None:False,}
def edit_account_preferences_web(request):
    """
       Edits account preferences for the account
                  Parameters:
                      request.PUT has a form for editing account preferences
                  Returns:
                      JSONRequest with success message and edited Account Preferences instance or error message
    """
    if request.method == 'POST':
        acc = request.user.accounts.get(account_id=request.session['account_id'])
        # acc_pref = acc.account_preferences
        # acc_pref.delete()
        form = PreferencesForm(request.POST)
        # TODO add in checking for dashes!
        # This error below is gone bc I no longer check if form is valid
        print(form.errors) # TODO <ul class="errorlist"><li>home_page<ul class="errorlist"><li>Account_ preferences with this Home page already exists.</li></ul></li></ul>

        home_page = request.POST.get('home_page')
        if(home_page == ''):
            print("This is the fix")
            request.session['err_message'] = "Please select a homepage"

        acc_pref = acc.account_preferences
        home_page = acc.sites.get(id=home_page)
        acc_pref.home_page = home_page
        acc_pref.sync_enabled = CHECKBOX_MAPPING[request.POST.get('sync_enabled')]
        acc_pref.searchable_profile = CHECKBOX_MAPPING[request.POST.get('searchable_profile')]
        acc_pref.cookies_enabled = CHECKBOX_MAPPING[request.POST.get('cookies_enabled')]
        acc_pref.popups_enabled = CHECKBOX_MAPPING[request.POST.get('popups_enabled')]
        acc_pref.is_dark_mode = CHECKBOX_MAPPING[request.POST.get('is_dark_mode')]
        acc_pref.save()
        print(acc_pref.sync_enabled)
        print("acc_pref", acc_pref)
        request.session['message'] = "Account Preferences Saved"
    return redirect('/profile')

@login_required
def shared_folders_web(request):
    curr_user = request.user
    curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
    folders = curr_account.shared_folders.all()

    # make these autocorrect on typing?
    folder_form = SharedFolder()
    folder_form.fields['bookmarks'].queryset = curr_account.bookmarks.all()
    folder_form.fields['tabs'].queryset = curr_account.tabs.all()
    folder_form.fields['notes'].queryset = curr_account.notes.all()
    folder_form.fields['collaborators'].queryset = curr_account.friends.all()
    folder_form.fields['collaborators'].initial = curr_account

    if ('message' in request.session):
        message = request.session['message']
        del request.session['message']
        messages.success(request, message)
    elif ('err_message' in request.session):
        message = request.session['err_message']
        del request.session['err_message']
        messages.error(request, message)

    return render(request, "flexr_web/shared_folders.html", {"Folders": folders, "folder_form": folder_form, "curr_acc": curr_account })

@login_required
def shared_folder_individual_web(request, pk):
    current_acc = request.user.accounts.get(account_id = request.session['account_id'])
    shared_folder = current_acc.shared_folders.get(id = pk)
    owner = shared_folder.owner
    #CHANGE THIS TO NOT USE THE SHARED FOLDERS COLLABORATORS, this was written this way for testing the view method
    collaborators = shared_folder.collaborators.all()
    print(collaborators)
    tabs = shared_folder.tabs.all()
    print(tabs)
    bookmarks = shared_folder.bookmarks.all()
    notes = shared_folder.notes.all()

    # if a tab, bookmark, note is in the shared folder. Then the way we have the api's set up the user that doesn't own the object will now not be able to view, edit, or delete the object
    # we may want to add a field to each object that says "shared"

    # return render(request, "flexr_web/shared_folder.html", {"SharedFolder": shared_folder, "Collaborators": collaborators, "Tabs": tabs, "Bookmarks": bookmarks, "Notes": notes})
    return render(request, "flexr_web/shared_folder.html", {"shared_folder": shared_folder, "Collaborators": collaborators, "Tabs":tabs, "Bookmarks": bookmarks, "Notes": notes, "curr_acc":current_acc})

@login_required
def create_shared_folder_web(request):
    # Change required fields on the form.
    if request.method == 'POST':
        form = SharedFolder(request.POST)
        if form.is_valid():
            # form.save()
            print(request.POST)
            title = form.cleaned_data['title']
            desc = form.cleaned_data['description']
            owner = request.user.accounts.get(account_id = request.session['account_id'])
            collaborators =  form.cleaned_data['collaborators']
            tabs = form.cleaned_data['tabs']
            notes = form.cleaned_data['notes']
            bookmarks = form.cleaned_data['bookmarks']
            folder = sharedFolder.objects.create(title = title, description = desc, owner = owner)
            folder.collaborators.set(collaborators)
            folder.tabs.set(tabs)
            folder.notes.set(notes)
            folder.bookmarks.set(bookmarks)

            folder.save()
            request.session['message'] = "Shared Folder created"
        else:
            request.session['err_message'] = "Shared Folder not created."
            print(form.errors)
        return redirect('/shared_folders')

@login_required
def create_bookmark_folder_web(request):
    form = BookmarkFolderForm(request.POST)

    # check that the form is valid
    if form.is_valid():
        # form.save()
        #print(request.POST)

        # grab information from the form
        title = form.cleaned_data['title']
        owner = request.user.accounts.get(account_id = request.session['account_id'])
        bookmarks = form.cleaned_data['bookmarks']

        # create shared folder object and set its attributes
        folder = bookmarkFolder.objects.create(title = title, owner = owner)
        folder.bookmarks.set(bookmarks)
        folder.save()

    # request message for debugging
        request.session['message'] = "Bookmark Folder created"

    else:
        request.session['err_message'] = "Bookmark Folder not created."
        #print(form.errors)

    # return to shared folders page
    return redirect('/bookmarks')

@login_required
def delete_bookmark_folder_web(request, pk):
    current_acc = request.user.accounts.get(account_id = request.session['account_id'])
    obj = current_acc.bookmark_folders.get(id = pk)
        # delete note object
    obj.delete()

        # return to notes page
    return redirect('/bookmarks')

@login_required
def notes_hub_web(request):
    curr_user = request.user
    print(curr_user)
    curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
    print(curr_account)
    accounts = curr_user.accounts.all()
    notes = curr_account.notes.all()
    form = notef
    if ('message' in request.session):
        message = request.session['message']
        del request.session['message']
        messages.success(request, message)
    elif ('err_message' in request.session):
        message = request.session['err_message']
        del request.session['err_message']
        messages.error(request, message)

    return render(request, "flexr_web/notes.html", {"Notes": notes, "Accounts": accounts, 'form': form, "curr_acc": curr_account})

# need args
@login_required
def note_individual_web(request, pk):
    curr_user = request.user
    print(curr_user)
    curr_account = curr_user.accounts.get(account_id=request.session['account_id'])
    print(curr_account)
    obj = curr_account.notes.get(pk=pk)
    accounts = curr_user.accounts.all()
    form = EditNoteForm()
    form.fields['title'].initial = obj.title
    form.fields['content'].initial = obj.content

    if ('message' in request.session):
        message = request.session['message']
        del request.session['message']
        messages.success(request, message)
    elif ('err_message' in request.session):
        message = request.session['err_message']
        del request.session['err_message']
        messages.error(request, message)

    locked = obj.lock
    if('note_unlocked' in request.session):
        id = request.session['note_unlocked']
        if( id == obj.id):
            locked = False
        del request.session['note_unlocked']

    return render(request, "flexr_web/note.html", {"object": obj, 'form': form, "accounts": accounts, "locked": locked, "curr_acc":curr_account})

@login_required
def bookmarks_hub_web(request):
    return None

@login_required
def bookmark_individual_web(request):
    return None

@login_required
def browsing_history_web(request):
    curr_user = request.user
    print(curr_user)
    curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
    print(curr_account)
    accounts = curr_user.accounts.all()
    history = curr_account.history.all()
    form = FilterHistoryForm
    
    return render(request, "flexr_web/browsing_history.html", {"History": history, "Accounts": accounts, "form": form, "curr_acc":curr_account})

@login_required
def browsing_history_filter(request):
    curr_user = request.user
    curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
    accounts = curr_user.accounts.all()
    form = FilterHistoryForm

    # grab date and time information from POST form
    start_date = request.POST['start_date']
    start_time = request.POST['start_time']
    end_date = request.POST['end_date']
    end_time = request.POST['end_time']

    # concat to datetime format
    start_datetime = start_date + ' ' + start_time
    end_datetime = end_date + ' ' + end_time

    # construct datetime object with timezone
    # TODO: Gerald check that timezone's work correctly
    start = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M').replace(tzinfo = pytz.UTC)
    end = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M').replace(tzinfo = pytz.UTC)
    

    # filter history based on given start and end datetimes
    history = curr_account.history.filter(
        visit_datetime__gte=start,
        visit_datetime__lte=end
    )

    # this returns a new webpage, but probably shouldn't
    # can we just edit the current webpage?
    return render(request, "flexr_web/browsing_history.html", {"History": history, "Accounts": accounts, "form": form, "curr_acc":curr_account})

@login_required
def active_tabs_web(request):
    curr_user = request.user
    print(curr_user)
    curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
    print(curr_account)
    accounts = curr_user.accounts.all()
    tabs = curr_account.tabs.all()
    if ('message' in request.session):
        message = request.session['message']
        del request.session['message']
        messages.success(request, message)
    elif ('err_message' in request.session):
        message = request.session['err_message']
        del request.session['err_message']
        messages.error(request, message)
    return render(request, "flexr_web/open_tabs.html", {"Tabs":tabs, "Accounts": accounts, "curr_acc":curr_account})


@login_required
def add_bookmark_web(request, id):
    curr_user = request.user
    curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
    accounts = curr_user.accounts.all()
    tabs = curr_account.tabs.all()

    tab = curr_account.tabs.get(pk = id)
    Bookmark.create_bookmark(tab, curr_account)
    request.session['message'] = "Bookmark Created"
    return redirect('/open_tabs')

def delete_bookmark_web(request, id):
    curr_user = request.user
    curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
    Bookmark.delete_bookmark(id)
    request.session['message'] = "Bookmark Deleted"
    return redirect('/bookmarks')


@login_required
def bookmarks_web(request):
    curr_user = request.user
    curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
    bookmarks = curr_account.bookmarks.all()
    if ('message' in request.session):
        message = request.session['message']
        del request.session['message']
        messages.success(request, message)
    elif ('err_message' in request.session):
        message = request.session['err_message']
        del request.session['err_message']
        messages.error(request, message)
    return render(request, "flexr_web/bookmarks.html", {"Bookmarks": bookmarks, "curr_acc":curr_account})


def friends(request):
    curr_account = request.user.accounts.get(account_id = request.session['account_id'])
    friends = curr_account.friends.all()
    print(friends)
    return render(request, "flexr_web/friends.html", {"Friends": friends})

def add_friend(request):
    friend_acc_id = request.POST.get('account_friend')
    friend_account = Account.objects.get(account_id = friend_acc_id)
    user_account = request.user.accounts.get(account_id = request.session['account_id'])
    friend_request = Friendship.objects.get_or_create(sent = user_account, received = friend_account)
    return redirect('/friends')

# class FriendViews(DetailView):

def deny_friend(request, pk):
    friend_request = Friendship.objects.get(id = pk)
    friend_request.status = "Declined"
    friend_request.save()
    request.session['message'] = "Friend request DENIED"
    return redirect('/profile')

def accept_friend(request, pk):
    friend_request = Friendship.objects.get(id = pk)
    friend_request.status = "Accepted"
    friend_request.save()
    request.session['message'] = "Friend request ACCEPTED"
    return redirect('/profile')

def remove_notif(request, pk):
    curr_account = request.user.accounts.get(account_id = request.session['account_id'])
    notif = curr_account.notifs.get(id = pk)
    curr_account.notifs.remove(notif)
    curr_account.save()
    return redirect('/')

def remove_friend(request, pk):
    current_account = request.user.accounts.get(account_id = request.session['account_id'])
    friend_account = Account.objects.get(account_id=pk)

    current_account.all_friends.remove(friend_account)
    friend_account.all_friends.remove(current_account)
    friendship = Friendship.objects.filter(sent = current_account, received = friend_account)
    if(friendship.count() == 0):
        friendship = Friendship.objects.filter(sent = friend_account, received = current_account)
        if(friendship.count() == 0):
            request.session['errmessage'] = "Trouble finding friendship"
            return redirect('/profile')
    friendship = friendship[0]
    friendship.status = "Declined"
    friendship.save()
    current_account.save()
    friend_account.save()
    request.session['message'] = "Friend deleted"
    return redirect('/profile')

################## REST API Endpoints ##################


################## Managing User  ##################

def sign_up(request):
    """
    Creates the User in the database, allowing them to sign in
          :param:
              request.POST that has the user information
          :return:
              JSONRequest with success and user data or error message
    """
    return None

def login(request): 
    """
    Takes in a form and checks the database against the provided username and password to provide access to the app
          :param:
              request
          :return:
              JSONRequest with success or error message
    """
    return None

def logout(request):
    """
    Logs the user out of flexr. Erases session data and does not allow access
          :param:
              request
          :return:
              JSONRequest with success or error message
    """
    logout(request)
    return redirect('login')

    # return None

def check_status(request):
    """
    Checks whether a user is logged in or not
          :param:
              request
          :return:
              JSONRequest with a logged in or logged out message
    """

##################  Managing Account ##################

#TODO This needs to be turned into a class based view like the TabViews

# def account_manager(request): # we should use these
class AccountView(LoginRequiredMixin, DetailView):
    def get(self, request, *args, **kwargs):
        """
        Adds an account to the user's profile
              :param:
                  request
              :return:
                  JSONRequest with requested account or an error message
        """
        
        account = request.user.accounts.filter(pk = kwargs["id"])

        # if empty
        if not account:
            return HttpResponse(f'Account with id={kwargs["id"]} not found.', status=404)

        data = AccountSerializer(account[0])
        return JsonResponse(data.data, safe=False)

        
    # TODO: Gerald
    # Session keys
    def patch(self, request, *args, **kwargs):
        """
        Switches the current account that the user is on. This data is stored in a django session key
              :param:
                  request
              :return:
                  JSONRequest with success or error message
        """


        account = request.user.accounts.filter(pk = kwargs["id"])

        # if empty
        if not account:
            return HttpResponse(f'Account with id={kwargs["id"]} not found.', status=404)

        request.session["account_id"] = kwargs["id"]
        messages.success(self.request, 'Account patched', extra_tags='alert')

        return HttpResponse(f'Switched to Account {kwargs["id"]}')


    def post(self, request, *args, **kwargs):
        """
        Adds an account to the user's profile
               :param:
                  request.PUT has a form for a created account
               :return:
                  JSONRequest with success or error message
        """
        data = request.POST.dict()
        acc = Account.objects.create(user = request.user,  **data)
        
        if acc:
            return HttpResponse("Account created.")
        else:
            return HttpResponse("Error occurred.", status=404)

    def put(self, request, *args, **kwargs):
        """
        Take in a form from the user that edits the information of the account
               :param:
                  request.PUT has an id for an account and the new account data
               :return:
                  JSONRequest with success or error message
        """
        data = json.loads(request.body)
        result = request.user.accounts.filter(pk = kwargs["id"]).update(**data)
        
        if result:
            return HttpResponse(f"Updated account with id: {kwargs['id']}")
        else:
            return HttpResponse(f"Account with id: {kwargs['id']} not found", status=404)

    def delete(self, request, *args, **kwargs):
        """
        Deletes an account from a user's profile
                   :param:
                      request.DELETE has an id for an account
                  :return:
                      JSONRequest with success or error message
        """

        result = request.user.accounts.get(pk = kwargs["id"]).delete()
       
        if result:
            return HttpResponse(f"Deleted account with id: {kwargs['id']}")
        else:
            return HttpResponse(f"Account with id: {kwargs['id']} not found", status=404)

##################  Managing tabs  ##################

class AllTabsView(LoginRequiredMixin, ListView):

    def get_queryset(self):
        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id = self.request.session['account_id'])
        return Tab.objects.filter(account = curr_account)

    def get(self, *args, **kwargs):
        """
              Gets all tabs from the current account (request.user.account.tabs.all())
                        :param:
                            request.GET has a type that says all
                        :return:
                            JSONRequest with all tab instances or error message
        """
        tabs = self.get_queryset()
        tab_list = list(tabs)
        # print(tab_list)
        return HttpResponse(tabs)

class TabView(LoginRequiredMixin, DetailView):

    def get_queryset(self):
        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id= self.request.session['account_id'])
        return Tab.objects.filter(account = curr_account)

    # This method is used to get a single tab
    def get(self, *args, **kwargs):
        """
        Looks in the tab table for the instance. If it's not there then it deletes it
                  :param:
                      request.GET has tab id or url
                  :return:
                      JSONRequest with tab data
        """
        tab = self.get_queryset().filter(pk = kwargs["id"])[0]
        # print(self.tab)
        curr_account = Account.objects.filter(user = self.request.user)[0]
        message = Tab.visit_tab(kwargs["id"], curr_account)
        data = TabSerializer(tab)
        return JsonResponse(data.data, safe=False)

    # This method is used to close a tab
    def delete(self, request, *args, **kwargs):
        """
        Closes a specifc tab, deletes from tab table
                  :param:
                      request.DELETE has the tab id
                  :return:
                      JSONRequest with success or error message
        """
        tab = self.get_queryset().filter(pk = kwargs["id"])[0]
        
        #curr_user = request.user
        #curr_account = curr_user.accounts.get(account_id= request.session['account_id'])
        #tab = Tab.objects.filter(account = curr_account).filter(pk = kwargs["id"])
        tab.delete()
        return HttpResponse("worked")

    def post(self, request, *args, **kwargs):
        """
       Looks in the site table for an instance; uses that instance or creates a new one if one doesn't exist to
       create a tab instance in the tab table
                 :param:
                     request.PUT has information for a tab like url
                 :return:
                     JSONRequest with success or error message
       """
        #print(self.request.session)
        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id=self.request.session['account_id'])
        message = "sucess"
        site_url = request.POST.get("url")
        print(request.POST)
        tab = Tab.open_tab(site_url = site_url, curr_account= curr_account)
        return HttpResponse(message)

def add_tab(request):
    curr_user = request.user
    curr_account = curr_user.accounts.get(account_id= request.session['account_id'])
    message = ""
    site_url = request.POST.get("url")
    print(request.POST)
    tab = Tab.open_tab(site_url = site_url, curr_account=curr_account)
    request.session['message'] = "Tab added"
    return redirect('/')

# This opens the tab from a site
@login_required
def open_tab(request, *args, **kwargs):
    print("Tab opening")
    curr_user = request.user
    curr_account = curr_user.accounts.get(account_id=request.session['account_id'])
    message = ""
    try:
        site_url = curr_account.sites.get(id = kwargs['id']).url
        print(request.POST)
        tab = Tab.open_tab(site_url=site_url, curr_account=curr_account)
        request.session['message'] = "Tab added"
    except:
        request.session['err_message'] = "Tab could not be opened"
    return redirect('/')

@login_required
def close_tab(request, *args, **kwargs):
    curr_user = request.user
    curr_account = curr_user.accounts.get(account_id=request.session['account_id'])
    message = ""
    try:
        tab = curr_account.tabs.get(id = kwargs['id'])
        print(tab)

        tab = Tab.close_tab( tabID = kwargs['id'], curr_account = curr_account)
        print(tab)
        request.session['message'] = "Tab closed"
    except:
        request.session['err_message'] = "Tab could not be closed"
    return redirect('/') # TODO we should set up django sesions to know where to redirect a user based on previous page


################## Managing shared folders ##################

def get_all_shared_folders(request):
    """
    Gets all shared folders from the current account (request.user.account.sharedfolders.all())
              :param:
                  request.GET has a type that says all
              :return:
                  JSONRequest with all shared folder instances or error message
    """
    return None

def get_individual_shared_folder(request):
    """
    Creates a shared folder in the shared table. Adds all users to it along with any current objects
              :param:
                  request.GET has an id for a shared folder
              :return:
                  JSONRequest with success message and folder object or error message
    """
    return None

def create_shared_folder(request):
    """
    Creates a shared folder in the shared table. Adds all users to it along with any current objects
              :param:
                  request.POST has form for a shared folder
              :return:
                  JSONRequest with success message and folder object or error message
    """
    return None

def add_account_to_shared_folder(request):
    """
    Creates a shared folder in the shared table. Adds all users to it along with any current objects
              Parameters:
                  request.PUT has an id for an account and an id for a shared folder
              Returns:
                  JSONRequest with success or error message
    """
    return None

def edit_shared_folder(request):
    """
    Edits a shared folder in the shared table
              Parameters:
                  request.PUT has an id for a shared folder and a form with new folder data
              Returns:
                  JSONRequest with success message and the new folder instance or error message
    """
    return None

def delete_shared_folder(request):
    """
    Deletes a shared folder in the shared table
                  Parameters:
                      request.DELETE has an id for a shared folder
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def remove_account_from_shared_foler(request):
    """
        Removes a specific account from a shared folder in the shared table
                  Parameters:
                      request.PUT has an id for a shared folder and an id for an account
                  Returns:
                      JSONRequest with success or error message
    """

    return None

def add_tab_to_shared_folder(request):
    """
        Adds a specific tab to a shared folder in the shared table
                  Parameters:
                      request.PUT has an id for a shared folder and an id for a tab
                  Returns:
                      JSONRequest with success message and a tab instance or error message
    """

    return None

def remove_tab_from_shared_folder(request):
    """
        Adds a specific note to a shared folder in the shared table
                  Parameters:
                      request.PUT has an id for a shared folder and an id for a tab
                  Returns:
                      JSONRequest with success message or error message
    """
    return None


#  does a note get added to a shared folder
def add_note_to_shared_folder(request):
    """
        Adds a specific note to a shared folder in the shared table
                  Parameters:
                      request.PUT has an id for a shared folder and an id for a note
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def remove_note_from_shared_folder(request):
    """
        Removes a specific note from a shared folder in the shared table
                  Parameters:
                      request.PUT has an id for a shared folder and an id for a note
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def add_bookmark_to_shared_folder(request):
    """
        Adds a specific bookmark to a shared folder in the shared table
                  Parameters:
                      request.PUT has an id for a shared folder and an id for a bookmark
                  Returns:
                      JSONRequest with success message and the bookmark instance or error message
    """
    return None

def remove_bookmark_from_shared_folder(request):
    """
        Removes a specific bookmark to a shared folder in the shared table
                  Parameters:
                      request.PUT has an id for a hsared folder and an id for a bookmark
                  Returns:
                      JSONRequest with success or error message
    """
    return None


##################   Managing History ##################

# filtering on andriod side
# need filtering for webclient also

class HistoryView(LoginRequiredMixin, DetailView):

    def get(self, request, *args, **kwargs):
        url = request.path.split('/')

        if url[-1] == 'filter':
            return self.filter_history(request, *args, **kwargs)
        else:
            return self.get_history(request, *args, **kwargs)



    def get_history(self, request, *args, **kwargs):
        """
        Gets all site history from the current account
                Parameters:
                    request.GET has an id for a site history
                Returns:
                    JSONRequest with success message and the SiteHistory instance or error message
        """
        #print('test')
        history = History.objects.filter(account = kwargs["id"])
        data = HistorySerializer(history, many=True)
        return JsonResponse(data.data, safe=False)

    def filter_history(self, request, *args, **kwargs):
        """
        Returns filtered all site history from the current account
                Parameters:
                    request.GET has a JSON object that has the filter type and typed
                Returns:
                    JSONRequest with success message and the SiteHistory objects or error message
        """

        payload = request.GET.dict()
        history = History.objects.filter(
            account = kwargs["id"],
            visit_datetime__gte=payload['datetime_from'],
            visit_datetime__lte=payload['datetime_to'])
        data = HistorySerializer(history, many=True)
        return JsonResponse(data.data, safe=False)

    def delete(self, request, *args, **kwargs):
        url = request.path.split('/')

        if url[-1] == 'filter':
            return self.delete_history_range(request, *args, **kwargs)
        else:
            return self.delete_all_history(request, *args, **kwargs)

    def delete_history_range(self, request, *args, **kwargs):
        """
        Deletes all history from a user within a given range
                Parameters:
                    request.DELETE has a JSON object that has a date range
                Returns:
                    JSONRequest with success message and the SiteHistory objects or error message
        """
        payload = json.loads(request.body)
        history = History.objects.filter(
            account = kwargs["id"],
            visit_datetime__gte=payload['datetime_from'],
            visit_datetime__lte=payload['datetime_to']).delete()

        return HttpResponse(f'{history} History objects removed')

    def delete_all_history(self, request, *args, **kwargs):
        """
        Deletes all history from a user
                Parameters:
                    request.DELETE
                Returns:
                    JSONRequest with success message or error message
        """

        history = History.objects.all().delete()

        return HttpResponse(f'{history} History objects removed')



##################  Managing Bookmarks ##################

def add_bookmark(request):
    """
        Adds a bookmark to a bookmark table for the specific account
                  Parameters:
                      request.PUT has a form for data for a bookmark
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def remove_bookmark(request):
    """
        Removes a bookmark from a bookmark table for the specific account
                  Parameters:
                      request.DELETE has an id for a bookmark
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def edit_bookmark(request):
    """
        Edits a bookmark from a bookmark table for the specific account
                  Parameters:
                      request.PUT has a form for data for the edited bookmark
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def get_bookmark(request):
    """
       Gets a specific bookmark from a bookmark table for the specific account
                  Parameters:
                      request.GET has an id for a bookmark
                  Returns:
                      JSONRequest with success message and a bookmark or error message
    """
    return None

def remove_all_bookmarks(request):
    """
       Removes all bookmark from a bookmark table for the specific account
                  Parameters:
                      request.DELETE has an id for a bookmark
                  Returns:
                      JSONRequest with success or error message
    """
    return None


##################  Managing Account Preferences ##################


def edit_account_preferences(request):
    """
       Edits account preferences for the account
                  Parameters:
                      request.PUT has a form for editing account preferences
                  Returns:
                      JSONRequest with success message and edited Account Preferences instance or error message
    """
    return None

def get_account_preferences(request):
    """
       Gets all account preferences for the account
                  Parameters:
                      request.GET has an id for account prefernces
                  Returns:
                      JSONRequest with success message and account preferences instance or error message
    """
    return None


##################  Managing Notes ##################

def create_note(request):

    if request.method == 'POST':
        form = notef(request.POST)
        # print("Note made")
        if form.is_valid():
            acc = request.user.accounts.get(account_id = request.session['account_id'])
            tit = request.POST.get('title')
            cont = request.POST.get('content')
            lo = request.POST.get('lock')
            passw = request.POST.get('password')
            if lo == 'on':
                lo = True
            else:

                if (passw not in EMPTY_VALUES):
                    print("reached",passw)
                    request.session['err_message'] = "Note not created. Please put a password on locked note"
                    return redirect('/notes')
                lo = False

            newnote = Note.objects.create(account=acc, title=tit, content=cont, lock=lo, password=passw)
            newnote.save()
            request.session['message'] = "Note created"
        else:
            request.session['err_message'] = "Note not created. Please put a password on locked note"
            print(form.errors)

        return redirect('/notes')

    """
       Creates note for the account
                  Parameters:
                      request.PUT has a form for a new note
                  Returns:
                      JSONRequest with success message and Note instance or error message
    """
    return None

def delete_note(request, pk):
    obj = Note.objects.get(pk=pk)
    obj.delete()
    return redirect('/notes')
    return render(request, "flexr_web/notes.html")
    """
       Deletes note for the account
                  Parameters:
                      request.DELETE has an id for a note
                  Returns:
                      JSONRequest with success message or error message
    """
    return None

def edit_note(request, pk):
    if request.method == 'POST':
        form = EditNoteForm(request.POST)
        print("Note edited")
        if form.is_valid():
            title = request.POST.get('title')
            content = request.POST.get('content')
            curr_acc = Account.objects.get(account_id = request.session['account_id'])
            obj = curr_acc.notes.get(pk=pk)
            obj.title = title
            obj.content = content
            obj.save()
            request.session['message'] = "Note edited"
        request.session['err_message'] = "Note could not be edited"
    return redirect('/opennote/'+str(obj.id))


    """
       Edit note for the account
                  Parameters:
                      request.PUT has a form for a Note
                  Returns:
                      JSONRequest with success message and the Note instance or error message
    """
    # return None

def unlock_note(request, pk):
    current_acc = request.user.accounts.get(account_id = request.session['account_id'])
    form_password = request.POST.get('password')
    note = current_acc.notes.get(pk = pk)

    if(note.password == form_password):
        request.session['note_unlocked'] = pk
        request.session['message'] = "Note unlocked"
    else:
        request.session['err_message'] = "Wrong password"

    return redirect('/opennote/' + str(pk))


def get_note(request):
    """
       Gets note for the account
                  Parameters:
                      request.GET has an id for a Note
                  Returns:
                      JSONRequest with success message and the Note instance or error message
    """
    return None

def get_all_notes(request):
    """
       Gets all notes for the account
                  Parameters:
                      request.GET
                  Returns:
                      JSONRequest with success message and all note instances or error message
    """
    return None


from django.shortcuts import render
# from .models import *
# Create your views here.

# from django.http import HttpResponse, JsonResponse



# def get_tab():
#     """Gets all open tabs from the database for the user.
#
#     Parmeters:
#         request(not sure type): Built in django thing that makes stuff easy"""

    # return None

# def pushkin(request):
#     return HttpResponse("Hello, world. This is Pushkin!")


# def index(request):
#     # help(get_tab)
#     # print(get_tab.__doc__)
#     # return HttpResponse("Hello, world. This is Flexr!")
#     # tyler = Account.objects.create()
#     # tyler.save()
#
#     return render(request, "index.html")

# url = "/tab/<id>"
#
# 127.0.0.1/tab/3283

# def get_account(request, *args, **kwargs):
#     account = Account.objects.filter(id = kwargs["id"])[0]
#     print(account)
#     response = JsonResponse({"account": account})
#     return response


# Features List
# Multitasking
    # Allows users to view multiple websites simultaneously
    # Supports media playback and viewing
    # Allows media to play in the background while only viewing one website
    # Backend server running on the cloud
    # Allows users to create and login to account within the mobile application
    # Allows users to login to their account through a web-application to view their personal browsing data and notes
    # Handles syncing preferences and notes across devices

# Note taking
    # Allows users to take structured and unstructured notes within the application
    # Allows users the ability to password protect notes
    # Shareable notes and browser data
    # Ability to share notes and browsing data between friends/family/co-workers
    # Enables users to join teams to easily share browser data and notes in real time

# Security Features
    # Automatically filters out malicious websites
    # Blocks unwanted pop-up websites
    # Verifies website certificates
    # Browsing anonymously in private browsing mode
    # Navigation history will not be saved while in private browsing mode
    # Cookies will be deleted upon exiting private browsing mode

#  create user
# edit user
#  delete user
#

# create , read, edit, delete
# POST, GET, PUT, DELETE

# 2 types of methods that we need in views
# Type 1 will server the website pages
# Type 2 will be REST API calls


# Process of visiting a site
# urser 23421 gives url facebook.com

# Search for user 23421
# filter user 23421 sites for facebook.com
# edit last_visit
# increment number of visits
# update site_ranking
# create SiteHistory for Site
# create Tab for Site
# set Tab status
# return success or error message


# Process for bookmarking
# user 23421 bookmarks facebook.com
# Search for user 23421
# filter user 23421 sites for facebook.com
# Create Bookmark instance for facebook.com
# update site_ranking




