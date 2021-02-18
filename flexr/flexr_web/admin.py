from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(User)
admin.site.register(Account)
admin.site.register(Team)
admin.site.register(Site)
admin.site.register(Tab)
admin.site.register(Bookmark)
admin.site.register(Device)
admin.site.register(Account_Preferences)
admin.site.register(Note)