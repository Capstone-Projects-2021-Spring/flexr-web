from django.contrib.auth.models import User
from django.core.validators import RegexValidator  # used for phone number and email checks in regex
from django.db import models
from datetime import datetime

# Create your models here.

# TODO research how much storage we will need on the AWS server
# TODO research the difference between ForeignKey, ForeignObject, ManyToManyField, OneToOneField, OneToMany, ManyToOne

# possibly use django user/auth for this?
# TODO research whether this should be here or in admin.py (maybe same for accounts)

class Account(models.Model):
    # user.accounts.all() this is how you get all accounts within the user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts")  # not sure if this is how we do this

    # check the snytax on the email field
    email = models.EmailField(verbose_name="Email Address", max_length=50)  # can you add verification to a model field?

    # below code from https://stackoverflow.com/questions/19130942/whats-the-best-way-to-store-phone-number-in-django-models
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)  # validators should be a list

    date_joined = models.DateTimeField()  # look up parameters
    type_of_account = models.CharField(verbose_name="Type of account", max_length=50,
                                       choices=(("Business", "Business"),
                                                ("Personal", "Personal"),
                                                ("Kids", "Kids"),
                                                ("Private", "Private"),
                                                ("Other", "Other")))

    # TODO add a default profile picture
    # profile_picture = models.ImageField(default="/static/img/profile_pic.jpg") # not sure if this is the correct path
    #TODO research what on_delete = models.CASCADE does
    #
    # not sure if next two should be foreignkeys
    # suggested_sites = models.ForeignKey()  # TODO need to make a method for suggested_tabs
    # current_tabs = models.ForeignKey() # TODO need a method for this
    teams = models.ManyToManyField("Team", blank=True, null = True)
    friends = models.ManyToManyField("Account", blank=True, null = True)
    # devices = models.ForeignKey("Device", on_delete=models.CASCADE, blank=True, null = True)
    account_preferences = models.OneToOneField("Account_Preferences", on_delete=models.CASCADE, blank=True, null = True)
    account_id = models.AutoField(primary_key=True)

    def save(self,  *args, **kwargs):
        if self.pk is None: #new users
            self.account_preferences = Account_Preferences.objects.create()
            super().save(*args, **kwargs)  # Call the "real" save() method.

    def __str__(self):
        return "UserID:" + str(self.user.id) + "." + str(self.account_id)+ " " + str(self.user.username) + " " + str(self.type_of_account)
    # def __str__(self):
    #     return str(self.user.first_name) + " " + str(self.user.last_name) + ": " + str(self.type_of_account)


class Team(models.Model):
    team_name = models.CharField(verbose_name="Team name", max_length=50)
    created_date = models.DateTimeField()
    status = models.CharField(verbose_name="Status of team", max_length=50, choices=(("Active", "Active"), ("Inactive", "Inactive")))
    # The type of team offers different levels
    type_of_team = models.CharField(verbose_name="Type of team", max_length=50, choices=(("Parental guidance", "Parental guidance"),
                                                                          ("Friends/Family", "Friends/Family"),
                                                                          ("Work", "Work")))
    members = models.ManyToManyField(Account) #map this to accounts

    def __str__(self):
        return str(self.team_name)


class SiteHistory(models.Model):
    site = models.ForeignKey("Site", on_delete=models.CASCADE, related_name="site_history")
    account = models.ForeignKey("Account", on_delete=models.CASCADE, related_name="history")
    visit_datetime = models.DateTimeField()
    def __str__(self):
        return "User " + str(self.account.account_id)+ ": " + str(self.visit_datetime) + " " + str(self.site.url)

# this is not set up to be history the way I originally intended need to make another object for history
class Site(models.Model):
    # Account.Objects.get(account_id = accountObject).site_set.all()
    account = models.ForeignKey("Account", on_delete=models.CASCADE, related_name="sites") #this collection of sites is the history
    # maybe use validators instead?
    url = models.URLField()
    first_visit = models.DateTimeField()
    last_visit = models.DateTimeField()
    recent_frequency = models.IntegerField()  # number of visits in the last week #TODO need to write a method for this
    number_of_visits = models.IntegerField()  # keeps track of number of visits
    open_tab = models.BooleanField(verbose_name="Is this site opened in a tab?")
    bookmarked = models.BooleanField(verbose_name="Is this site bookmarked?")
    def __str__(self):
        return str(self.url)

# when a site is visited the url of the site will be used to search through all tabs
# may have to think about
# this is used to keep track of all open tabs. User has option to easily close these tabs
class Tab(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="tabs")

    # TODO add logic to add a site and create the tab from that site
    # should this be a one to many field?
    # I'm not sure if site is mapped here correctly
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="tabs") # you can have several tabs of the same site open
    created_date = models.DateTimeField()
    # the next two attributes are to suggest a closing of the tab
    # TODO we should implement a setting to have tabs automatically deleted after a certain amount of time
    last_visited = models.DateTimeField() #maybe add auto now to this
    # TODO research if there is a way to make choice field more strict
    # TODO Have this be a choice field
    # TODO make the status of a tab calculated using a method
    status = models.CharField(verbose_name= "Status of the tab", max_length=50) # once tab becomes inactive a notification gets sent to close or it autmatically closes?
    # TODO change tab status in the Site model on save

    def __str__(self):
        return str(self.site.url)


# Should we have a window class? this would probably be handled by the android app

class Bookmark(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="bookmarks")
#     Does a bookmark need to be attached to an account or can it be standalone and the account just attaches to the bookmark
#     should a bookmark model be mapped to a tab?
    bookmark_name = models.CharField(verbose_name= "Bookmark name", max_length=50)
    created_date = models.DateTimeField() #keeps track of creation date
    # TODO research if the bookmark gets deleted if the site will then be deleted
    site = models.OneToOneField(Site, on_delete=models.CASCADE) #if the site gets deleted the bookmark gets deleted
    last_visited = models.DateTimeField() #keeps track of last visited date
    recent_frequency = models.IntegerField() # number of visits in the last week
    number_of_visits = models.IntegerField()# keeps track of number of visits

    def __str__(self):
        return str(self.bookmark_name)

# TODO change bookmark status in the Site model on save

#
# What is the message handler?

# this class may be pointless

class Device(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="devices")
    name = models.CharField(verbose_name= "Device name", max_length=25)
    # This could help with security?
    date_added = models.DateTimeField()
    # type_of_device #thinking an option for desktop, mobile, tablet? don't know how this would be useful?
    # status = models.CharField  # thinking a choice field here to say when the last time that a device was used
    device_id = models.AutoField(primary_key = True)

    def __str__(self):
        return str(self.name)

# Do we need security model? Could probably just put it in settings

# need to make sure this deletes when account gets deleted
class Account_Preferences(models.Model):
    name = models.CharField(default="Account Preferences", max_length=10)
    home_page = models.OneToOneField(Site, on_delete=models.CASCADE, null= True, blank=True)

    # sync
    sync_enabled = models.BooleanField(default=True) # not sure if this is possible or useful
    # sharing
    searchable_profile = models.BooleanField(default=True)
    # security
    cookies_enabled = models.BooleanField(default=True)
    popus_enabled = models.BooleanField(default=True)
    # maybe split into device preferences too?
    # Misc
    #   home page

    # Display?
    #     Dark mode
    #     font-size

    # syncing
    #   sync_on?

    # sharing
    #   searchable profile?
    # security
        # Cookies
        # Popups
    def __str__(self):
       return str(self.name) + " " +str(self.id)

# I don't know how to model a structured note
#TODO add attributes to model a structured note
class Note(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="notes")
    # title = models.CharField(verbose_name="Note title", max_length=100, default="note_"+str(datetime.date()))
    title = models.CharField(verbose_name="Note title", max_length=100, default="note")
    created_date = models.DateTimeField()
    content = models.TextField(verbose_name= "Note content")
    lock = models.BooleanField(verbose_name="Is note password protected?" , default=False)
    password = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return str(self.title)