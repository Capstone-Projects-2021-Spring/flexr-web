from django.urls import path

from . import views
from .views import *

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
    path('close_tab/<id>', views.close_tab, name = "close tab")

    #path('shared_folder/', ) TODO
    # TODO For note.html
]
