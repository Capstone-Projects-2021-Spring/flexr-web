from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
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
# Create your views here.

################## Managing Website Pages ##################

class IndexView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # account = serializers.serialize("json", Account.objects.all() )
        # print("Account: ", account)
        # sites = serializers.serialize("json", account.sites.all())
        # print("Sites: ", sites)
        # tab = serializers.serialize("json", account.tabs.all())
        # print("Tabs: ", tab)
        # history = account.history.all()[0] #serializers.serialize("json", account.history.all()[0])
        # print(history)
        # print(history.site)
        # print(history.site.site_ranking)
        # return HttpResponse(account, sites, tab, history)
        # response = JsonResponse({'account': account, "sites": sites,
        #                          "tab": tab, "history": history})
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
        # suggested_sites = curr_account.suggested_sites()
        print(curr_user)
        if ('account_message' in self.request.session):
            message = self.request.session['account_message']
            print("message")
            del self.request.session['account_message']
            messages.success(self.request, message)
        print("reached")

        form = AccountForm
        return render(self.request, "flexr_web/index.html",
                      {"curr_acc": curr_account, "Accounts": accounts, "Sites": sites, "Tabs": tabs, "Notes": notes,
                       "History": history, "Bookmarks": bookmarks,
                       "form": form})
# @login_required()
# def index(request):
#     # account = serializers.serialize("json", Account.objects.all() )
#     # print("Account: ", account)
#     # sites = serializers.serialize("json", account.sites.all())
#     # print("Sites: ", sites)
#     # tab = serializers.serialize("json", account.tabs.all())
#     # print("Tabs: ", tab)
#     # history = account.history.all()[0] #serializers.serialize("json", account.history.all()[0])
#     # print(history)
#     # print(history.site)
#     # print(history.site.site_ranking)
#     # return HttpResponse(account, sites, tab, history)
#     # response = JsonResponse({'account': account, "sites": sites,
#     #                          "tab": tab, "history": history})
#     curr_user = request.user
#     curr_account = curr_user.accounts.all()[0]
#     accounts = curr_user.accounts.all()
#     history = curr_account.history.all()
#     sites = curr_account.sites.all()
#     tabs = curr_account.tabs.all()
#     bookmarks = curr_account.bookmarks.all()
#
#     print(curr_user)
#     return render(request, "flexr_web/index.html", {"Accounts": accounts, "Sites": sites, "Tabs": tabs,
#

@csrf_exempt
def switch_account(request,*args, **kwargs):
    request.session['account_id'] = kwargs["id"]
    print("switching account....")
    request.session['account_message'] = "Account Switched"
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
            user = authenticate(username=username, password=password)
            new_account = Account.objects.create(user=user, email=user.email, username = user.username)
            new_account.save()
            request.session['account_id'] = new_account.account_id
            return redirect('/')
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
            return redirect('/')

@login_required
def edit_account_web(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
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
    acc_pref.save()
    print(acc_pref)
    initial_dict = {
        "home_page": curr_account.account_preferences.home_page,
    }
    pref_form = PreferencesForm(initial=initial_dict)
    print(pref_form)
    return render(request, "flexr_web/profile.html", {"current_account":curr_account, "Accounts": accounts, "Preferences":acc_pref, "pref_form": pref_form})

def edit_account_preferences_web(request):
    """
       Edits account preferences for the account
                  Parameters:
                      request.PUT has a form for editing account preferences
                  Returns:
                      JSONRequest with success message and edited Account Preferences instance or error message
    """
    if request.method == 'POST':
        form = PreferencesForm(request.POST)
        if form.is_valid():
            form.save()

    return redirect('/profile')

@login_required
def shared_folders_web(request):
    return None

@login_required
def shared_folder_individual_web(request):
    shared_folder = request.shared_folder
    owner = shared_folder.owner
    #CHANGE THIS TO NOT USE THE SHARED FOLDERS COLLABORATORS, this was written this way for testing the view method
    collaborators = folder.collaborators
    
    return render(request, "flexr_web/shared_folder.html", {"SharedFolder": shared_folder, "Collaborators": collaborators})

@login_required
def notes_hub_web(request):
    curr_user = request.user
    print(curr_user)
    curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
    print(curr_account)
    accounts = curr_user.accounts.all()
    notes = curr_account.notes.all()
    form = notef

    return render(request, "flexr_web/notes.html", {"Notes": notes, "Accounts": accounts, 'form': form})

# need args
@login_required
def note_individual_web(request, pk):
    obj = Note.objects.get(pk=pk)
    return render(request, "flexr_web/note.html", {"object": obj})

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
    
    return render(request, "flexr_web/browsing_history.html", {"History": history, "Accounts": accounts, "form": form})

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
    

    # filter history based on given state and end datetimes
    history = curr_account.history.filter(
        visit_datetime__gte=start,
        visit_datetime__lte=end
    )

    # this returns a new webpage, but probably shouldn't
    # can we just edit the current webpage?
    return render(request, "flexr_web/browsing_history.html", {"History": history, "Accounts": accounts, "form": form})

@login_required
def active_tabs_web(request):
    curr_user = request.user
    print(curr_user)
    curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
    print(curr_account)
    accounts = curr_user.accounts.all()
    tabs = curr_account.tabs.all()
    return render(request, "flexr_web/open_tabs.html", {"Tabs":tabs, "Accounts": accounts})


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
        messages.success(self.request, 'Natalie has a fat ass <3333', extra_tags='alert')

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
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
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
        curr_account = curr_user.accounts.get(account_id=request.session['account_id'])
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
        return HttpResponse(tab)

    # This method is used to close a tab
    def delete(self, *args, **kwargs):
        """
        Closes a specifc tab, deletes from tab table
                  :param:
                      request.DELETE has the tab id
                  :return:
                      JSONRequest with success or error message
        """
        tab = self.get_queryset().filter(pk = kwargs["id"])[0]
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
        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id=request.session['account_id'])
        message = ""
        site_url = request.POST.get("url")
        message = Tab.open_tab(site_url = site_url, curr_account= curr_account)
        return HttpResponse(message)


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
        print("Note made")
        if form.is_valid():
            curr_acc = request.user.accounts.get(account_id = request.session['account_id'])
            form.save()
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

def edit_note(request):
    """
       Edit note for the account
                  Parameters:
                      request.PUT has a form for a Note
                  Returns:
                      JSONRequest with success message and the Note instance or error message
    """
    return None

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




