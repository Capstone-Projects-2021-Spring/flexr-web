from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    # path('flexr_login', views.flexr_login, name='flexr_login')
]
