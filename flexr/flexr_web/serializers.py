from rest_framework import serializers

from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ['account_id', 'user', 'username', 'email', 'phone_number', 'date_joined', 'type_of_account',
        'account_preferences', 'account_id']

class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['id', 'name', 'account', 'suggested_sites', 'url', 'first_visit', 'last_visit', 'recent_frequency',
                  'number_of_visits', 'site_ranking', 'open_tab', 'bookmarked']

class TabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tab
        fields = ['id', 'account', 'site','url', 'created_date', 'last_visited', 'status']

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['id', 'site','url', 'account', 'visit_datetime']

class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ['id', 'account','url', 'bookmark_name', 'created_date', 'site', 'last_visited',
        'recent_frequency', 'number_of_visits']

class AccountPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account_Preferences
        fields = ['id','name', 'home_page','home_page_url', 'sync_enabled', 'searchable_profile',
        'cookies_enabled', 'popups_enabled', 'is_dark_mode']

### TODO: These models need to be finalized
class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'account', 'title', 'created_date', 'content', 'lock', 'password']

class Device(serializers.ModelSerializer):
    class Meta:
        pass

class SharedFolderSerializer(serializers.ModelSerializer):
    collaborators = AccountSerializer(many=True, read_only=True)
    bookmarks = BookmarkSerializer(many = True, read_only=True)
    tabs = TabSerializer(many=True, read_only=True)
    notes = NoteSerializer(many = True, read_only=True)
    class Meta:
        model = sharedFolder
        fields = ['id', 'title', 'description', 'collaborators', 'bookmarks', 'tabs', 'notes']

class FriendshipSerializer(serializers.ModelSerializer):
    sent = AccountSerializer(many=False, read_only=True)
    received = AccountSerializer(many=False, read_only=True)
    class Meta:
        model = Friendship
        fields = ['id','sent', 'received', 'status', 'sent_date', 'accepted_date']
