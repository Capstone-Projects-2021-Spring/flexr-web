from rest_framework import serializers

from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ['user', 'username', 'email', 'phone_number', 'date_joined', 'type_of_account',
        'account_preferences', 'account_id']

class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['name', 'account', 'suggested_sites', 'url', 'first_visit', 'last_visit', 'recent_frequency',
                  'number_of_visits', 'site_ranking', 'open_tab', 'bookmarked']

class TabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tab
        fields = ['account', 'site', 'created_date', 'last_visited', 'status']

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['site', 'account', 'visit_datetime']

class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ['account', 'bookmark_name', 'created_date', 'site', 'last_visited',
        'recent_frequency', 'number_of_visits']

class AccountPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account_Preferences
        fields = ['name', 'home_page', 'sync_enabled', 'searchable_profile ', 
        'cookies_enabled ', 'popups_enabled ', 'is_dark_mode ']

### TODO: These models need to be finalized
class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        pass

class Device(serializers.ModelSerializer):
    class Meta:
        pass

class SharedFolderSerializer(serializers.ModelSerializer):
    class Meta:
        pass
