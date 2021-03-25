from django.urls import path

from . import views
from .views import *

# Gerald: probably a better way to do this, but I'm dumb
from .class_views.AccountView import AccountViewWeb
from .class_views.AccountView import AccountViewAPI
from .class_views.BookmarksView import BookmarksView, BookmarksViewAPI
from .class_views.HistoryView import HistoryView, HistoryViewAPI
from .class_views.IndexView import IndexView
from .class_views.NoteView import NoteView
from .class_views.NotesView import NotesView
from .class_views.ProfileView import ProfileView
from .class_views.SharedFolderView import SharedFolderView
from .class_views.SharedFoldersView import SharedFoldersView
from .class_views.TabsView import TabsView
from .class_views.UserView import UserAPIView
from .class_views.FriendView import FriendView
from .class_views.SiteView import SiteAPIView

urlpatterns = [
    path('register', views.register_web, name='register'),

    path('', IndexView.as_view(), name='index'), #broken

    path('add_account/', AccountViewWeb().add_account, name = "add account"),
    path('switch_account/<id>', AccountViewWeb().switch_account, name = "switch account"),

    path('browsing_history/', HistoryView.as_view(), name='history'),
    path('filter_history/', HistoryView().filter, name = "filter history"),

    path('notes/', NotesView.as_view(), name='notes'), #broken
    path('create_note', NotesView().create_note, name='create_note'),
    path('note/<int:pk>/', NoteView.as_view(), name='note-detail'),
    path('delete-note/<int:pk>/', NotesView().delete_note, name='delete_note'),

    path('opennote/<int:pk>', NoteView.as_view(), name='note-detail'), #broken
    path('edit_note/<int:pk>', NoteView().edit_note, name='edit_note'),
    path('unlock_note/<int:pk>/', NoteView().unlock_note, name='unlock note'),

    path('open_tabs/', TabsView.as_view(), name='tabs'), #broken
    path('add_tab/', TabsView().add_tab, name = "add tab"),
    #path('open_tab/', TabsView().open_tab, name = "open tab"),
    path('close_tab/<id>', TabsView().close_tab, name = "close tab"),

    path('bookmarks/', BookmarksView.as_view(), name = "bookmarks"), #broken
    path('add_bookmark/<id>/', BookmarksView().add_bookmark, name = "add bookmark"),
    path('delete_bookmark/<id>/', BookmarksView().delete_bookmark, name = "delete bookmark"),

    path('shared_folders/', SharedFoldersView.as_view(), name = "shared folders"),
    path('add_shared_folder/', SharedFoldersView().create_shared_folder, name = "add shared folder"),

    path('shared_folder/<int:pk>/', SharedFolderView.as_view(), name = "shared folder"),

    path('profile/', ProfileView.as_view(), name='profile'), #broken
    path('edit_account/', ProfileView().edit_account, name="edit account"),
    path('edit_preferences/', ProfileView().edit_account_preferences, name = "edit account preferences"),

    
    path('friends/', FriendView.as_view(), name = "friends"),
    path('add_friend/', FriendView().add_friend, name = "add friend"),
    path('deny_friend/<int:pk>', FriendView().deny_friend, name = "deny friend"),
    path('accept_friend/<int:pk>', FriendView().accept_friend, name="accept friend"),
    path('remove_friend/<int:pk>', FriendView().remove_friend, name="remove friend"),
    path('remove_notif/<int:pk>', FriendView().remove_notif, name="remove notif"),

    #API Endpoints

    path('api/login/', UserAPIView().login),
    path('api/register/', UserAPIView().sign_up),
    path('api/logout/', UserAPIView().logout),
    path('api/status/', UserAPIView().check_status),

    path('api/site/', SiteAPIView.as_view()),

    path('api/tabs/', AllTabsView.as_view()),
    path('api/tab/<id>', TabView.as_view()),
    path('api/tab/open', TabView.as_view()),
    path('api/tab/open', TabView.as_view()),

    path('api/account/<id>', AccountViewAPI.as_view()),
    path('api/accounts/', AccountViewAPI.as_view()),
    path('api/account/<int:pk>/switch/', AccountViewAPI().switch_account, name = "switch account"),

    path('api/history/<id>', HistoryViewAPI.as_view()),
    path('api/history/<id>/filter', HistoryViewAPI.as_view()),

    path('api/bookmarks/', BookmarksViewAPI.as_view()),
    path('api/bookmarks/<id>', BookmarksViewAPI.as_view()),
    path('api/bookmarks/all', BookmarksViewAPI.as_view()),

]

# old patterns
''' 
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('register', views.register_web, name='register'),
    path('profile/', views.profile_web, name='profile'),
    path('open_tabs/', views.active_tabs_web, name='tabs'),
    path('notes/', views.notes_hub_web, name='notes'),
    path('browsing_history/', views.browsing_history_web, name='history'),
    path('api/tabs/', AllTabsView.as_view()),
    path('api/tab/<id>', TabView.as_view()),
    path('api/tab/', TabView.as_view()),
    path('create_note', create_note, name='create_note'),
    path('edit_note/<int:pk>', edit_note, name='edit_note'),
    path('opennote/<int:pk>/', views.note_individual_web, name='note-detail'),
    path('delete-note/<int:pk>/', views.delete_note, name='delete_note'),
    path('unlock_note/<int:pk>/', views.unlock_note, name='unlock note'),
    path('api/account/<id>', AccountView.as_view()),
    path('api/account/', AccountView.as_view()),
    path('switch_account/<id>', views.switch_account, name = "switch account" ),
    path('add_account/', views.add_account_web, name = "add account"),
    path('edit_account/', views.edit_account_web, name="edit account"),
    path('edit_preferences/', views.edit_account_preferences_web, name = "edit account preferences"),
    path('api/history/<id>', HistoryView.as_view()),
    path('api/history/<id>/filter', HistoryView.as_view()),
    path('filter_history/', views.browsing_history_filter, name = "filter history"),
    path('add_tab/', views.add_tab, name = "add tab"),
    path('open_tab/', views.open_tab, name = "open tab"),
    path('close_tab/<id>', views.close_tab, name = "close tab"),
    path('add_bookmark/<id>/', views.add_bookmark_web, name = "add bookmark"),
    path('delete_bookmark/<id>/', views.delete_bookmark_web, name = "delete bookmark"),
    path('bookmarks/', views.bookmarks_web, name = "bookmarks"),
    path('shared_folders/', views.shared_folders_web, name = "shared folders"),
    path('shared_folder/<int:pk>/', views.shared_folder_individual_web, name = "shared folder"),
    path('add_shared_folder/', views.create_shared_folder_web, name = "add shared folder"),

    path('friends/', views.friends, name = "friends"),
    path('add_friend/', views.add_friend, name = "add friend"),
    path('deny_friend/<int:pk>', views.deny_friend, name = "deny friend"),
    path('accept_friend/<int:pk>', views.accept_friend, name="accept friend"),
    path('remove_friend/<int:pk>', views.remove_friend, name="remove friend"),

    # TODO For note.html
]
'''
