from django.contrib import admin
from .models import *

# Inline done with this https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#inlinemodeladmin-objects

class TabInLine(admin.TabularInline):
    model = Tab

class HistoryInLine(admin.TabularInline):
    model = History

class SiteInLine(admin.TabularInline):
    model = Site

class BookmarkInLine(admin.TabularInline):
    model = Bookmark

class DeviceInLine(admin.TabularInline):
    model = Device

class NoteInLine(admin.TabularInline):
    model = Note

class AccountAdmin(admin.ModelAdmin):
    inlines = [
        TabInLine, HistoryInLine, SiteInLine, BookmarkInLine, DeviceInLine, NoteInLine,
    ]


# Register your models here.
admin.site.register(Account, AccountAdmin)
admin.site.register(Team)
admin.site.register(History)
admin.site.register(Site)
admin.site.register(Tab)
admin.site.register(Bookmark)
admin.site.register(Device)
admin.site.register(Account_Preferences)
admin.site.register(Note)
