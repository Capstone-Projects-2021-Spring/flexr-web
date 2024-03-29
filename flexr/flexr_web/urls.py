from django.urls import path

from . import views
from .class_views.AccountPreferencesView import AccountPreferencesAPIView
from .class_views.SuggestedSitesView import SuggestedSiteAPIView
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
from .class_views.BookmarkFolderView import BookmarkFolderView, BookmarkFoldersViewAPI
from .class_views.SharedFoldersView import SharedFoldersView
from .class_views.TabsView import TabsView, TabAPIView
from .class_views.UserView import UserAPIView
from .class_views.FriendView import FriendViewWeb, FriendAPIView
from .class_views.SiteView import SiteAPIView
from .class_views.NoteView import NoteViewAPI
from .class_views.SharedFolderView import FoldersViewAPI

urlpatterns = [
    path('register', views.register_web, name='register'),

    path('', IndexView.as_view(), name='index'), #broken

    path('add_account/', AccountViewWeb().add_account, name = "add account"),
    path('switch_account/<id>/', AccountViewWeb().switch_account, name = "switch account"),
    path('delete_account/<int:pk>/', AccountViewWeb().delete, name="delete account"),

    path('browsing_history/', HistoryView.as_view(), name='history'),
    path('browsing_history/delete/', HistoryView().delete, name='delete history'),

    path('notes/', NotesView.as_view(), name='notes'), #broken
    path('search_notes/', NotesView().search_note, name='search_notes'), #broken
    path('create_note/', NotesView().create_note, name='create_note'),
    path('note/<int:pk>/', NoteView.as_view(), name='note-detail'),
    path('delete-note/<int:pk>/', NotesView().delete_note, name='delete_note'),

    path('opennote/<int:pk>/', NoteView.as_view(), name='note-detail'), #broken
    path('edit_note/<int:pk>/', NoteView().edit_note, name='edit_note'),
    path('unlock_note/<int:pk>/', NoteView().unlock_note, name='unlock note'),

    path('open_tabs/', TabsView.as_view(), name='tabs'), #broken
    path('add_tab/', TabsView().add_tab, name = "add tab"),
    path('close_tab/<id>/', TabsView().close_tab, name = "close tab"),

    path('bookmarks/', BookmarksView.as_view(), name = "bookmarks"), #broken
    path('add_bookmark/<id>/', BookmarksView().add_bookmark, name = "add bookmark"),
    path('delete_bookmark/<id>/', BookmarksView().delete_bookmark, name = "delete bookmark"),
    # path('delete_bookmark/<id>/', BookmarksView().delete_bookmark, name = "delete bookmark"),

    path('create_bookmark_folder/', BookmarkFolderView().create_bookmark_folder_web, name='create_bookmark_folder'),
    path('bookmark_folder/<int:pk>/', BookmarkFolderView.as_view(), name='bookmark-folder-detail'),
    path('delete_bookmark_folder/<int:pk>/', BookmarkFolderView().delete_bookmark_folder_web, name='delete-bookmark-folder'),
    path('edit_bookmark_folder/<int:pk>', BookmarkFolderView().edit_bookmark_folder, name='edit_bookmark_folder'),
                        #bookmark id / bookmark_folder_pk
    path('remove_from_folder/<int:id>/<int:pk>/', BookmarkFolderView().remove_from_folder, name='remove_from_folder'),
    path('bookmark_folder/<id>/add_bookmark/', BookmarkFolderView().add_bookmark, name = "add bookmark bookmark"),


    path('shared_folders/', SharedFoldersView.as_view(), name = "shared folders"),
    path('add_shared_folder/', SharedFoldersView().create_shared_folder, name = "add shared folder"),
    path('delete_shared_folder/<int:pk>/', SharedFoldersView().delete_shared_folder, name = "delete_shared_folder"),
    path('edit_shared_folder/<int:pk>/', SharedFolderView().edit_shared_folder, name = "edit_shared_folder"),

    path('shared_folder/<int:pk>/', SharedFolderView.as_view(), name = "shared folder"),
    path('shared_folder/<id>/add_collaborator/', SharedFolderView().add_collaborator, name = "add collaborator"),
    path('shared_folder/<id>/remove_collaborator/', SharedFolderView().remove_collaborator, name = "remove collaborator"),
    path('shared_folder/<id>/add_note/', SharedFolderView().add_note, name = "add note"),
    path('shared_folder/<id>/remove_note/', SharedFolderView().remove_note, name = "remove note"),
    path('shared_folder/<id>/add_tab/', SharedFolderView().add_tab, name = "add tab"),
    path('shared_folder/<id>/remove_tab/', SharedFolderView().remove_tab, name = "remove tab"),
    path('shared_folder/<id>/add_bookmark/', SharedFolderView().add_bookmark, name = "add bookmark"),
    path('shared_folder/<id>/remove_bookmark/', SharedFolderView().remove_bookmark, name = "remove bookmark"),


    path('profile/', ProfileView.as_view(), name='profile'), #broken
    path('edit_account/', ProfileView().edit_account, name="edit account"),
    path('edit_preferences/', ProfileView().edit_account_preferences, name = "edit account preferences"),

    
    path('friends/', FriendViewWeb.as_view(), name ="friends"),
    path('add_friend/', FriendViewWeb().add_friend, name ="add friend"),
    path('deny_friend/<int:pk>', FriendViewWeb().deny_friend, name ="deny friend"),
    path('accept_friend/<int:pk>', FriendViewWeb().accept_friend, name="accept friend"),
    path('remove_friend/<int:pk>', FriendViewWeb().remove_friend, name="remove friend"),
    path('remove_notif/<int:pk>', FriendViewWeb().remove_notif, name="remove notif"),

    #API Endpoints

    path('api/login/', UserAPIView().login),
    path('api/register/', UserAPIView().sign_up),
    path('api/logout/', UserAPIView().logout),
    path('api/status/', UserAPIView().check_status),

    path('api/site/', SiteAPIView.as_view()),
    path('api/suggested_sites/', SuggestedSiteAPIView.as_view()),

    path('api/tabs/', TabAPIView.as_view()),
    path('api/tab/<id>/', TabAPIView.as_view()),
    path('api/tab/<id>/visit/', TabAPIView().visit_tab),

    path('api/account/<id>/', AccountViewAPI.as_view()),
    path('api/accounts/', AccountViewAPI.as_view()),
    path('api/account/<id>/switch/', AccountViewAPI().switch_account, name = "switch account"),

    path('api/friendships/', FriendAPIView.as_view()),
    path('api/friendships/<id>/', FriendAPIView.as_view()),
    path('api/friendships/<id>/accept/', FriendAPIView().accept),
    path('api/friendships/<id>/deny/', FriendAPIView().deny),

    path('api/history/', HistoryViewAPI.as_view()),
    path('api/history/filter/', HistoryViewAPI.as_view()),
    path('api/history/<id>/', HistoryViewAPI.as_view()),
    #path('api/history/<id>/filter', HistoryViewAPI.as_view()),

    path('api/bookmarks/', BookmarksViewAPI.as_view()),
    path('api/bookmarks/<id>/', BookmarksViewAPI.as_view()),
    path('api/bookmarks/all/', BookmarksViewAPI.as_view()),

    path('api/bookmark_folders/', BookmarkFoldersViewAPI.as_view()),
    path('api/bookmark_folders/<id>/', BookmarkFoldersViewAPI.as_view()),

    path('api/account_preferences/', AccountPreferencesAPIView.as_view()),

    path('api/note/<id>/', NoteViewAPI.as_view()),
    path('api/notes/', NoteViewAPI.as_view()),

    path('api/shared_folders/', FoldersViewAPI.as_view()),
    path('api/shared_folders/<id>/', FoldersViewAPI.as_view()),
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
