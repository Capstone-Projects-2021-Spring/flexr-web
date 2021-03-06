from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register_web, name='register'),
    path('profile/', views.profile_web, name='register'),
]
