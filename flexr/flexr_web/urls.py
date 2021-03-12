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
    path('api/account/<id>', AccountView.as_view()),
    path('api/account/', AccountView.as_view()),
    path('switch_account/<id>', views.switch_account, name = "switch account" ),
    path('add_account/', views.add_account_web, name = "add account"),
    path('edit_account/', views.edit_account_web, name="add account")
    #path('shared_folder/', ) TODO
    # TODO For note.html
]
