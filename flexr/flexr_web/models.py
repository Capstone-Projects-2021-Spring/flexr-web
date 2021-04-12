from django.contrib.auth.models import User
from django.core.validators import RegexValidator  # used for phone number and email checks in regex
from django.db import models
from datetime import datetime
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum
# Create your models here.

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

        if self.account_preferences is None: #new users
            site = Site.objects.create(account=self, url="https://google.com")
            site.save()
            self.account_preferences = Account_Preferences.objects.create(home_page = site)

    def __str__(self):
        return str(self.username)+" #"+str(self.account_id)

    def rank_sites(self):
        # print("Ranking sites", self.sites.all())
        min_secdelta = 86400000
        max_freq = 1
        max_visits = 1
        for site in self.sites.all().iterator():
            secdelta = (timezone.now() - site.last_visit).days * 86400 # 1440 minutes in a day
            # this may be unnessesary
            site.recent_frequency = site.calculate_frequency()
            site.save()
            if secdelta < min_secdelta:
                min_secdelta = secdelta
            if site.recent_frequency > max_freq:
                max_freq = site.recent_frequency
            if site.number_of_visits > max_visits:
                max_visits = site.number_of_visits
        # print("Account.rank_sites: min_mindelta ",min_mindelta)
        # print("Account.rank_sites: max_freq ",max_freq)
        # print("Account.rank_sites: max_visits ",max_visits)
        for site in self.sites.all().iterator():
            secdelta = (timezone.now() - site.last_visit).days * 86400 # 1440 minutes in a day
            print((min_secdelta+.1)/(secdelta+.1))
            site.site_ranking = ((min_secdelta+1)/(secdelta+1))*(20)+(site.recent_frequency/max_freq)*(65)+(site.number_of_visits/ max_visits)*(15)
            site.site_ranking =(site.recent_frequency / max_freq) * (65) + (site.number_of_visits / max_visits) * (15)
            site.save()
            # print("Account.rank_sites: site.site_ranking: ",site, site.site_ranking)

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
        print("Account.rank_sites: suggested sites: ", self.suggested_sites.all())

# TODO get rid of this class once it is turned into shared_folder
class Team(models.Model):
    team_name = models.CharField(verbose_name="Team name", max_length=50)
    created_date = models.DateTimeField()
    status = models.CharField(verbose_name="Status of team", max_length=50, choices=(("Active", "Active"),
                                                                                     ("Inactive", "Inactive")))
    # The type of team offers different levels
    type_of_team = models.CharField(verbose_name="Type of team", max_length=50, choices=(
                                                                            ("Parental guidance", "Parental guidance"),
                                                                          ("Friends/Family", "Friends/Family"),
                                                                          ("Work", "Work")))
    members = models.ManyToManyField(Account) #map this to accounts

    def __str__(self):
        return str(self.team_name)

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
        # self.rank_site()
        # site_ranking = # update site ranking here

    def calculate_frequency(self):
        last_week =  timezone.now() - timedelta(days = 7)
        history = History.objects.filter(site = self,
                                         visit_datetime__gt = last_week)
        # print("Site.calculate_frequency ",history.count())
        freq = history.count()
        return freq

    # def rank_site(self):
    #     mindelta = (timezone.now() - self.last_visit).days * 1440 # 1440 minutes in a day
    #     print("Site rank_site: mindelta: ",mindelta)


    #TODO This needs to be implemented
    #Pseudocode for rankSite, a method that returns a number between 0 and 100, where the lower return value is the greater site ranking
    # def rankSite(self):
    #     if (self.number_of_visits > self.recent_frequency):
    #         return (self.recent_frequency/self.number_of_visits)*100
    #     else:
    #         return 0 #Should never get to this point, but if there are more reecent visits than total visits, this must be the highest ranked site

    def save(self, *args, **kwargs):
        # call super method to create Tab entry
        # print("URL: ", )
        url1 = str(self.url).split('?')[0]
        url2 = url1.split('/')
        #print("URL: ", url1 )
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
            
        return tab

    @classmethod
    def close_tab(cls, tabID, curr_account):
        try:
            # print("Models", tabID)
            tab = Tab.objects.filter(account = curr_account).get(id = tabID)
            tab.delete()
            return "successful"
        except Exception as e:
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
            return tab
        except Exception as e:
            return e

    def __str__(self):
        return str(self.site.url)

    
    def save(self, *args, **kwargs):
        # call super method to create Tab entry
        account = Account.objects.filter(pk = self.account_id)[0]
        site =  Site.objects.filter(pk = self.site_id)[0]
        self.url = self.site.url
        print("self.url", self.url)
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
    def create_bookmark(cls, tab, curr_account, last_visited=None):
        # try:
        bm = Bookmark.objects.create(account = curr_account, bookmark_name = tab.site.name, site=tab.site)
        bm.save()
        bm.site.bookmarked = bm.id
        print("Bookmark: create_bookmark", bm)
        bm.site.save()
        return bm.id
        # except:
        #     print('bookmark already exists')
        
    
    @classmethod
    def delete_bookmark(cls, id):
        bookmark = Bookmark.objects.get(id = id)
        bookmark.site.bookmarked = 0
        bookmark.site.save()
        bookmark = Bookmark.objects.filter(pk=id).delete()
        
        print('bookmark deleted')

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
        print(self.collaborators.all())

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
            try:
                self.sent.mutual_friends.remove(self.received)
            except:
                pass
            try:
                self.received.mutual_friends.remove(self.sent)
            except:
                pass
            sent_friends = self.sent.friends.exclude(account_id__in=self.received.friends.all()).exclude(
                user=self.sent.user)
            print("sent friends", sent_friends)
            # self.received.mutual_friends.add(sent_friends)
            for friend in sent_friends:
                self.received.mutual_friends.add(friend)
                friend.mutual_friends.add(self.sent)

            received_friends = self.received.friends.exclude(account_id__in=self.sent.friends.all()).exclude(
                user=self.received.user)
            print("received friends", received_friends)
            # self.sent.mutual_friends.add(received_friends)
            for friend in received_friends:
                self.sent.mutual_friends.add(friend)
                friend.mutual_friends.add(self.received)

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
