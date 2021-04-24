import os
import urllib
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.validators import RegexValidator  # used for phone number and email checks in regex
from django.db import models
from datetime import datetime

from django.utils import timezone
from datetime import datetime, timedelta
import favicon
from django.db.models import Sum
# Create your models here.
from urllib3 import response


class Account(models.Model):
    # user.accounts.all() this is how you get all accounts within the user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts")  # not sure if this is how we do this

    username = models.CharField(verbose_name="Username",max_length=15)
    # add a username?

    # check the snytax on the email field
    email = models.EmailField(verbose_name="Email Address", max_length=50)  # can you add verification to a model field?

    # below code from https://stackoverflow.com/questions/19130942/whats-the-best-way-to-store-phone-number-in-django-models
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)  # validators should be a list

    date_joined = models.DateTimeField(default=timezone.now)

    type_of_account = models.CharField(verbose_name="Type of account", max_length=50,
                                       choices=(("Business", "Business"),
                                                ("Personal", "Personal"),
                                                ("School", "School"),
                                                ("Private", "Private"),
                                                ("Kids", "Kids"),
                                                ("Other", "Other")),
                                        default = "Personal")
    # TODO add a default profile picture
    # profile_picture = models.ImageField(default="/static/img/profile_pic.jpg") # not sure if this is the correct path

    # TODO implement suggested_sites (see rank_site in the Site class)
    # suggested_sites = models.ForeignKey("Site", on_delete=models.CASCADE, related_name="suggested_sites", null = True)  # TODO need to make a method for suggested_tabs

    # TODO Pushkin: Change teams to shared_folders
    # teams = models.ManyToManyField("Team", blank=True, null = True) #I don't think this should be a manytomany field this should be a list of teams got by a method?
    # shared_folder = models.ManyToManyField("sharedFolder", blank=True, related_name = "shared_folders")

    friends = models.ManyToManyField("Account", related_name= "all_friends", blank=True) # this probably needs to be another table
    notifs = models.ManyToManyField("Friendship",  blank=True)
    pending_friends = models.ManyToManyField("Account", related_name="all_pending_friends",  blank=True)
    mutual_friends = models.ManyToManyField("Account", related_name="all_mutual_friends",  blank=True)

    account_preferences = models.OneToOneField("Account_Preferences", on_delete=models.CASCADE, blank=True, null = True)
    account_id = models.AutoField(primary_key=True)

    def save(self,  *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.
        print(self , ": Model: Account: save(): self.account_preferences: ", self.account_preferences)
        if self.account_preferences is None: #new users
            if(Site.objects.filter(account = self).count()>0):
                acc_pref = Account_Preferences.objects.create(home_page=Site.objects.filter(account = self)[0])
                acc_pref.save()
                self.account_preferences = acc_pref
            else:
                site = Site.objects.create(account=self, url="https://google.com")
                site.save()
                self.account_preferences = Account_Preferences.objects.create(home_page=site)
            print("NEW ACCOUNT: User "+self.user.username+"#"+str(self.user.id)+": created account: ", self)
        super().save()

    def __str__(self):
        return str(self.username)+" #"+str(self.account_id)

    def rank_sites(self):
        # print("Ranking sites", self.sites.all())
        min_secdelta = 86400000
        max_freq = 1
        max_visits = 1
        for site in self.sites.all().iterator():
            secdelta = (timezone.now() - site.last_visit).days * 86400 # 1440 minutes in a day
            # calculates frequency in the last week
            site.recent_frequency = site.calculate_frequency()
            site.save()
            if secdelta < min_secdelta:
                min_secdelta = secdelta
            if site.recent_frequency > max_freq:
                max_freq = site.recent_frequency
            if site.number_of_visits > max_visits:
                max_visits = site.number_of_visits

        # TODO: This needs to be optimized!
        for site in self.sites.all().iterator():
            secdelta = (timezone.now() - site.last_visit).days * 86400 # 1440 minutes in a day
            site.site_ranking = ((min_secdelta+1)/(secdelta+1))*(20)+(site.recent_frequency/max_freq)*(65)+(site.number_of_visits/ max_visits)*(15)
            site.site_ranking =(site.recent_frequency / max_freq) * (65) + (site.number_of_visits / max_visits) * (15)
            site.save()
            # print("Model: Account.rank_sites: site.site_ranking: ",site, site.site_ranking)

        for x in self.suggested_sites.all().iterator():
            self.suggested_sites.remove(x)
        #
        for x in self.sites.order_by('-site_ranking')[:5].iterator():
            self.suggested_sites.add(x)
        # print(self.suggested_sites.all())

        if(self.suggested_sites.all().count() < 5):
            # print("not enuf")
            for x in self.sites.all().iterator():
                self.suggested_sites.add(x)
        # print(self.suggested_sites.all())
        self.save()
        # for
        print("Model: Account.rank_sites(): suggested_sites: ", self.suggested_sites.all())

class History(models.Model):
    site = models.ForeignKey("Site", on_delete=models.CASCADE, related_name="site_history")
    account = models.ForeignKey("Account", on_delete=models.CASCADE, related_name="history") # don't do foreignkey here make it so that there is a method that gets the account from the site
    url = models.CharField(max_length=2500)
    visit_datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "histories"
        ordering = ('-visit_datetime',)

    def __str__(self):
        return "User " + str(self.account.account_id)+ ": " + str(self.visit_datetime) + " " + str(self.site.url)

    def save(self, *args, **kwargs):
        self.site.visited()
        self.url = self.site.url
        super().save()

class Site(models.Model):
    name = models.CharField(max_length=50)
    account = models.ForeignKey("Account", on_delete=models.CASCADE, related_name="sites") #this collection of sites is the history
    suggested_sites = models.ForeignKey("Account", on_delete=models.CASCADE, related_name="suggested_sites", blank=True, null = True)
    favicon_img_url = models.URLField(blank= True, null=True)
    url = models.URLField(max_length=2500)

    first_visit = models.DateTimeField(default=timezone.now) # need to put a method for this
    last_visit = models.DateTimeField(default=timezone.now) # need to put a method for this

    recent_frequency = models.IntegerField(default=0)  # number of visits in the last week #TODO need to write a method for this
    number_of_visits = models.IntegerField(default=1)  # keeps track of number of visits
    site_ranking = models.IntegerField(default=0) # uses a ranking algoithm to rank the sites

    # TODO Are these necessary?
    open_tab = models.BooleanField(verbose_name="Is this site opened in a tab?", default=True)
    bookmarked = models.IntegerField(verbose_name="Is this site bookmarked?", default = 0)

    # TODO Add functionality once a site is visited (check the Tab class)
    def visited(self):
        self.last_visit = timezone.now()
        self.recent_frequency = self.calculate_frequency()
        self.save()
        print("Model: Site: ",self,".visited()")
        # self.rank_site()
        # site_ranking = # update site ranking here

    def calculate_frequency(self):
        last_week =  timezone.now() - timedelta(days = 7)
        history = History.objects.filter(site = self,
                                         visit_datetime__gt = last_week)
        # print("Site.calculate_frequency ",history.count())
        freq = history.count()
        return freq

    def save(self, *args, **kwargs):
        # call super method to create Tab entry
        # print("URL: ", )
        if(self.name == None or self.name == "" or self.name == " "):
            try:
                req = requests.get(self.url)
                print("Site: save(): req.status_code: ", req.status_code)
                if(req.status_code == 200):
                    soup = BeautifulSoup(req.text, 'html.parser')
                    # print(soup.find_all('title')[0])
                    for title in soup.find_all('title'):
                        self.name = title.get_text()
                        print("Model: Site.save(): self.name: ", title.get_text())
                    try:
                        icons = favicon.get(self.url)
                        for i in icons:
                            if (i.format == "ico"):
                                req = requests.get(i.url)
                                if(req.status_code == 200):
                                    self.favicon_img_url = i.url
                                print("Model: Site.save(): self.favicon_img_url: ", i.url)
                    except:
                        pass
            except:
                pass
            if (self.name == "" or self.name == " " or req.status_code != 200):
                url1 = str(self.url).split('?')[0]
                url2 = url1.split('/')
                print("Model: Site.save(): url2: ", url2)
                try:
                    self.name = url2[2] + "/" + url2[3]
                except:
                    self.name = url2[2]


        super().save(*args, **kwargs)



    def __str__(self):
        return str(self.name)
    #TODO  make it so that the site creates an instance of browsing history on first call. Need to set up chain reactions for site history

# when a site is visited the url of the site will be used to search through all tabs
# this is used to keep track of all open tabs. User has option to easily close these tabs
class Tab(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="tabs") # use a method to get this fromt the site attribute

    # TODO add logic to add a site and create the tab from that site

    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="tabs") # you can have several tabs of the same site open
    created_date = models.DateTimeField(default=timezone.now)

    # TODO we should implement a setting to have tabs automatically deleted after a certain amount of time
    last_visited = models.DateTimeField(default=timezone.now) #maybe add auto now to this
    url = models.CharField(max_length=2500)

    # TODO Have this be a choice field
    # TODO make the status of a tab calculated using a method
    status = models.CharField(verbose_name= "Status of the tab", max_length=50) # once tab becomes inactive a notification gets sent to close or it autmatically closes?
    # TODO change tab status in the Site model on save

    #TODO Check the functionality of the methods below. Should have been tested but double check
    @classmethod
    def open_tab(cls, site_url, curr_account, first_visit=None, last_visit=None, toSave=True):
        if not first_visit:
            first_visit = timezone.now()
        if not last_visit:
            last_visit = timezone.now()

        try: # checks to see if the site already exists and opens tab
            site =  Site.objects.filter(account = curr_account).get(url = site_url)
            site.visited()
            tab = Tab(account = curr_account, site = site, status = "open")
            history = History.objects.create(account = curr_account, site = site, visit_datetime=last_visit)
            
        except: # if site doesn't exist create it and create tab
            site = Site.objects.create(account = curr_account , url = site_url, 
                first_visit=first_visit, last_visit=last_visit)
            tab = Tab(account = curr_account, site = site, status = "open")
            history = History.objects.create(account=curr_account, site=site, visit_datetime=last_visit)
            history.save()

        if toSave:
            tab.save()
        print("Model: Tab.open_tab(): tab: ", tab)
        return tab

    @classmethod
    def close_tab(cls, tabID, curr_account):
        try:
            # print("Models", tabID)
            tab = Tab.objects.filter(account = curr_account).get(id = tabID)
            tab.delete()
            print("Model: Tab.close_tab(): tab: ", tab)
            return "successful"
        except Exception as e:
            print("Model: Tab.close_tab(): tab: ERROR:", e)
            return e

    @classmethod
    def visit_tab(cls, tabID, curr_account):
        try:
            tab = Tab.objects.filter(account = curr_account).get(pk = tabID)
            tab.last_visited = datetime.now()
            status = "active"
            tab.save()
            site = Site.objects.filter(account=curr_account).get(url=tab.url)
            site.visited()
            history = History.objects.create(account=curr_account, site=site, visit_datetime=tab.last_visited)
            history.save()
            site = Site.objects.filter(account = curr_account).get(url = tab.url)
            print("Model: Tab.visit_tab(): tab: :", tab)
            return tab
        except Exception as e:
            print("Model: Tab.visit_tab(): tab: ERROR:", e)
            return e

    def __str__(self):
        return str(self.site.url)

    
    def save(self, *args, **kwargs):
        # call super method to create Tab entry
        account = Account.objects.filter(pk = self.account_id)[0]
        site =  Site.objects.filter(pk = self.site_id)[0]
        self.url = self.site.url
        print("Model: Tab.save(): self.url: ", self.url)
        super(Tab, self).save(*args, **kwargs)
        # create corresponding site object

class Bookmark(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="bookmarks")
    bookmark_name = models.CharField(verbose_name= "Bookmark name", max_length=50)
    created_date = models.DateTimeField(default=timezone.now) #keeps track of creation date
    site = models.ForeignKey(Site, on_delete=models.CASCADE) #if the site gets deleted the bookmark gets deleted
    last_visited = models.DateTimeField(default=timezone.now) #keeps track of last visited date
    recent_frequency = models.IntegerField(default=1) # number of visits in the last week
    number_of_visits = models.IntegerField(default=1)# keeps track of number of visits
    url = models.CharField(max_length=2500)

    # TODO create a visited method
    #TODO create a method to calculate frequency

    def __str__(self):
        return str(self.bookmark_name)

    @classmethod
    def create_bookmark(cls, site, curr_account, last_visited=None):
        # try:
        bm = Bookmark.objects.create(account = curr_account, bookmark_name = site.name, site=site)
        bm.save()
        site.bookmarked = bm.id
        print("Model: Bookmark.create_bookmark(): bm: ", bm)
        site.save()
        return bm.id
        # except:
        #     print('bookmark already exists')
        
    
    @classmethod
    def delete_bookmark(cls, id):
        bookmark = Bookmark.objects.get(id = id)
        bookmark.site.bookmarked = 0
        bookmark.site.save()
        print("Model: Bookmark.delete_bookmark(): bm: ", str(bookmark) + ": id: "+str(id))
        bookmark = Bookmark.objects.filter(pk=id).delete()

    def save(self, *args, **kwargs):
        # call super method to create Tab entry
        self.url =  self.site.url
        super().save(*args, **kwargs)

# TODO change bookmark status in the Site model on save
# Gerald: What is bookmark status?

# TODO need to make sure this deletes when account gets deleted (I think it does)
# TODO need to finalize the fields here
class Account_Preferences(models.Model):
    name = models.CharField(default="Account Preferences", max_length=10)
    home_page = models.ForeignKey(Site, on_delete=models.CASCADE, null= True)
    home_page_url = models.URLField()
    # sync
    sync_enabled = models.BooleanField(default=True) # not sure if this is possible or useful
    # sharing
    searchable_profile = models.BooleanField(default=True)
    # security
    cookies_enabled = models.BooleanField(default=True)
    popups_enabled = models.BooleanField(default=True)

    is_dark_mode = models.BooleanField(default=False)

    def __str__(self):
       return str(self.name) + " " +str(self.id)

    def save(self, *args, **kwargs):
        # call super method to create Tab entry
        self.home_page_url =  self.home_page.url
        super().save(*args, **kwargs)

class Note(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="notes")
    # title = models.CharField(verbose_name="Note title", max_length=100, default="note_"+str(datetime.date()))
    title = models.CharField(verbose_name="Note title", max_length=100, default="note")
    created_date = models.DateTimeField(default= timezone.now)
    content = models.TextField(verbose_name= "Note content") # https://pypi.org/project/django-richtextfield/#field-widget-settings
    lock = models.BooleanField(verbose_name="Is note password protected?" , default=False)
    password = models.CharField(max_length=40, blank=True)

    #TODO  Add a method here to unlock a note, Don't do this in views
    def __str__(self):
        return str(self.title)

#UNFINISHED
class sharedFolder(models.Model):
    #ownerAccount 
    #Title was going to have a CharField in place of Textfield, but I got the following error:
    #AttributeError: module 'django.db.models' has no attribute 'charField'
    title = models.CharField(verbose_name="Shared Folder Title", max_length=100)
    description = models.TextField(verbose_name="Shared Folder description")
    created_date = models.DateTimeField(default= timezone.now)
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="shared_folders")
    # TODO need to have this be a many to many field
    collaborators = models.ManyToManyField(Account, related_name="collab_shared_folders")
    bookmarks = models.ManyToManyField(Bookmark, blank=True)
    tabs = models.ManyToManyField(Tab , blank=True)
    notes = models.ManyToManyField(Note , blank=True)
    def __str__(self):
        return str(self.title)

    def save(self, *args, **kwargs):
        # call super method to create Tab entry
        super().save(*args, **kwargs)
        print("Model: sharedFolder.save(): self.collaborators: :", self.collaborators.all())

class bookmarkFolder(models.Model):
    title = models.CharField(verbose_name="Bookmark Folder Title", max_length=100)
    created_date = models.DateTimeField(default= timezone.now)
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="bookmark_folders")
    bookmarks = models.ManyToManyField(Bookmark, blank=True)

class Friendship(models.Model):
    sent = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="from_friend")
    received = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="to_friend")
    status = models.CharField(verbose_name="Status", max_length=50,
                                   choices=(("Accepted", "Accepted"),
                                            ("Pending", "Pending"),
                                            ("Declined", "Declined")),
                                   default="Pending")
    sent_date = models.DateTimeField(default= timezone.now)
    accepted_date = models.DateTimeField(blank = True, null=True)
    def __str__(self):
        return str(self.sent) + " -> " + str(self.received) + " | " + str(self.status)

    class Meta:
        ordering = ['sent_date']

    def save(self, *args, **kwargs):
        if(self.status == "Accepted" ):
            
            self.accepted_date = timezone.now()
            super().save(*args, **kwargs)

            # for friend in self.received.friends.all():
            #     if(self.sent.mutual_friends.filter(account_id = friend.account_id).count() == 0):
            #         self.sent.mutual_friends.add(friend)
            #         friend.mutual_friends.add(self.sent)
            #
            # for friend in self.sent.friends.all():
            #     if (self.received.mutual_friends.filter(account_id = friend.account_id).count() == 0):
            #         self.received.mutual_friends.add(friend)
            #         friend.mutual_friends.add(self.received)

            # for friend in self.received.friends.all():
            #
            # for friend in self.sent.friends.all():

            self.sent.friends.add(self.received)
            self.received.friends.add(self.sent)

            self.received.notifs.remove(self)
            self.sent.notifs.add(self)

            self.sent.pending_friends.remove(self.received)
            self.received.pending_friends.remove(self.sent)

            self.sent.save()
            self.received.save()

        elif (self.status == "Pending"):
            super().save(*args, **kwargs)
            self.received.notifs.add(self)
            self.sent.pending_friends.add(self.received)
            self.received.pending_friends.add(self.sent)
            self.sent.save()
            self.received.save()

        else:
            super().save(*args, **kwargs)
            self.received.notifs.remove(self)
            self.sent.pending_friends.remove(self.received)
            self.received.pending_friends.remove(self.sent)
            self.sent.save()
            self.received.save()
            self.delete()
