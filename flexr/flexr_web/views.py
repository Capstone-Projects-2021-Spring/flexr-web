from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from pydoc import *
from .forms import registrationform
from django.contrib.auth import authenticate, login

from .models import *
# Create your views here.

################## Managing Website Pages ##################

def index(request):


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
    # return HttpResponse("Hello, world. This is Flexr!")
    return render(request, 'index.html')
    # return response


def login_web(request):
    return None

def signup_web(request):
    return None

@login_required
def profile_web(request):
    return None

@login_required
def shared_folders_web(request):
    return None

@login_required
def shared_folder_individual_web(request):
    return None

@login_required
def notes_hub_web(request):
    return None

# need args
@login_required
def note_individual_web(request):
    return None

@login_required
def bookmarks_hub_web(request):
    return None

@login_required
def bookmark_individual_web(request):
    return None

@login_required
def browsing_history_web(request):
    return None

@login_required
def active_tabs_web(request):
    return None

@login_required
def devices_web(request):
    """
    Creates the User in the database, allowing them to sign in
            :param: request
            :return: JSONRequest with success or error message
    """
    return None

################## Managing User  ##################

def register(request):
    if request.method == 'POST':
        form = registrationform(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            return redirect('login')
    else:
        form = registrationform
    context = {'form' : form}
    return render(request, 'registration/register.html', context)

def sign_up(request):
    """
    Creates the User in the database, allowing them to sign in
          Parameters:
              request
          Returns:
              JSONRequest with success or error message
    """
    return None

def login(request):
    """
    Takes in a form and checks the database against the provided username and password to provide access to the app
          Parameters:
              request
          Returns:
              JSONRequest with success or error message
    """
    return None

def logout(request):
    """
    Logs the user out of flexr. Erases session data and does not allow access
          Parameters:
              request
          Returns:
              JSONRequest with success or error message
    """
    return None

def check_status(request):
    """
    Checks whether a user is logged in or not
          Parameters:
              request
          Returns:
              JSONRequest with success or error message
    """

##################  Managing Account ##################

# def account_manager(request): # we should use these

def get_account(request):
    """
    Adds an account to the user's profile
          Parameters:
              request
          Returns:
              JSONRequest with success or error message
    """

def switch_account(request):
    """
    Switches the current account that the user is on. This data is stored in a django session key
          Parameters:
              request
          Returns:
              JSONRequest with success or error message
    """
    return None

def add_account(request):
    """
    Adds an account to the user's profile
          Parameters:
              request
          Returns:
              JSONRequest with success or error message
    """
    return None

def edit_account(request):
    """
    Take in a form from the user that edits the information of the account
          Parameters:
              request
          Returns:
              JSONRequest with success or error message
    """
    return None

def delete_account(request):
    """
    Deletes an account from a user's profile
              Parameters:
                  request
              Returns:
                  JSONRequest with success or error message
    """
    return None

##################  Managing tabs  ##################

def open_tab(request):
    """
    Looks in the site table for an instance; uses that instance or creates a new one if one doesn't exist to
    create a tab instance in the tab table
              Parameters:
                  request
              Returns:
                  JSONRequest with success or error message
    """
    return None

def close_tab(request):
    """
    Closes a specifc tab, deletes from tab table
              Parameters:
                  request
              Returns:
                  JSONRequest with success or error message
    """
    return None

################## Managing shared folders ##################

def get_all_shared_folders(request):
    """
    Gets all shared folders from the current account (request.user.account.sharedfolders.all())
              Parameters:
                  request
              Returns:
                  JSONRequest with success or error message
    """
    return None

def get_individual_shared_folder(request):
    """
    Creates a shared folder in the shared table. Adds all users to it along with any current objects
              Parameters:
                  request
              Returns:
                  JSONRequest with success or error message
    """
    return None

def create_shared_folder(request):
    """
    Creates a shared folder in the shared table. Adds all users to it along with any current objects
              Parameters:
                  request
              Returns:
                  JSONRequest with success or error message
    """
    return None

def add_account_to_shared_folder(request):
    """
    Creates a shared folder in the shared table. Adds all users to it along with any current objects
              Parameters:
                  request
              Returns:
                  JSONRequest with success or error message
    """
    return None

def edit_shared_folder(request):
    """
    Edits a shared folder in the shared table
              Parameters:
                  request
              Returns:
                  JSONRequest with success or error message
    """
    return None

def delete_shared_folder(request):
    """
    Deletes a shared folder in the shared table
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def remove_account_from_shared_foler(request):
    """
        Removes a specific account from a shared folder in the shared table
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """

    return None

def add_tab_to_shared_folder(request):
    """
        Adds a specific tab to a shared folder in the shared table
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def remove_tab_from_shared_folder(request):
    """
        Adds a specific note to a shared folder in the shared table
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def add_note_to_shared_folder(request):
    """
        Adds a specific note to a shared folder in the shared table
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def remove_note_from_shared_folder(request):
    """
        Removes a specific note from a shared folder in the shared table
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def add_bookmark_to_shared_folder(request):
    """
        Adds a specific bookmark to a shared folder in the shared table
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def remove_bookmark_from_shared_folder(request):
    """
        Removes a specific bookmark to a shared folder in the shared table
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """
    return None


##################   Managing History ##################

# filtering on andriod side
# need filtering for webclient also

def get_history(request):
    """
    Gets all site history from the current account
              Parameters:
                  request
              Returns:
                  JSONRequest with success or error message
    """
    return None

def filter_history(request):
    """
    Returns filtered all site history from the current account
              Parameters:
                  request
              Returns:
                  JSONRequest with success or error message
    """
    return None

def delete_history_range(request):
    """
    Deletes all history from a user within a given range
              Parameters:
                  request
              Returns:
                  JSONRequest with success or error message
    """
    return None

def delete_all_history(request):
    """
    Deletes all history from a user
              Parameters:
                  request
              Returns:
                  JSONRequest with success or error message
    """
    return None


##################  Managing Bookmarks ##################

def add_bookmark(request):
    """
        Adds a bookmark to a bookmark table for the specific account
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def remove_bookmark(request):
    """
        Removes a bookmark from a bookmark table for the specific account
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def edit_bookmark(request):
    """
        Edits a bookmark from a bookmark table for the specific account
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def get_bookmark(request):
    """
       Gets a specific bookmark from a bookmark table for the specific account
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def remove_all_bookmarks(request):
    """
       Removes all bookmark from a bookmark table for the specific account
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """
    return None


##################  Managing Account Preferences ##################

def edit_account_preferences(request):
    """
       Edits account preferences for the account
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def get_account_preferences(request):
    """
       Gets all account preferences for the account
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """
    return None


##################  Managing Notes ##################

def create_note(request):
    """
       Creates note for the account
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def delete_note(request):
    """
       Deletes note for the account
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def edit_note(request):
    """
       Edit note for the account
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def get_note(request):
    """
       Gets note for the account
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
    """
    return None

def get_all_notes(request):
    """
       Gets all notes for the account
                  Parameters:
                      request
                  Returns:
                      JSONRequest with success or error message
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




