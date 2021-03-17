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

class NoteInLine(admin.TabularInline):
    model = Note

class SharedFolderInLine(admin.TabularInline):
    model = sharedFolder

class AccountAdmin(admin.ModelAdmin):
    inlines = [
        TabInLine, HistoryInLine, SiteInLine, BookmarkInLine, NoteInLine, SharedFolderInLine
    ]

class TabAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

# Register your models here.
admin.site.register(Account, AccountAdmin)
admin.site.register(sharedFolder)
admin.site.register(History)
admin.site.register(Site)
admin.site.register(Tab, TabAdmin)
admin.site.register(Bookmark)
admin.site.register(Account_Preferences)
admin.site.register(Note)
