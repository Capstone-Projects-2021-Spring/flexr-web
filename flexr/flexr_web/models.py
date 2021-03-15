from django.contrib.auth.models import User
from django.core.validators import RegexValidator  # used for phone number and email checks in regex
from django.db import models
from datetime import datetime
from django.utils import timezone
from datetime import datetime

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
    shared_folders = models.ManyToManyField("sharedFolder", blank=True)

    # friends = models.ManyToManyField("Account", blank=True, null = True) # this probably needs to be another table
    account_preferences = models.OneToOneField("Account_Preferences", on_delete=models.CASCADE, blank=True, null = True)
    account_id = models.AutoField(primary_key=True)


    def save(self,  *args, **kwargs):

        if self.pk is None: #new users
            self.account_preferences = Account_Preferences.objects.create()
        super().save(*args, **kwargs)  # Call the "real" save() method.

    def __str__(self):
        return str(self.username) + " " + str(self.type_of_account)

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
    visit_datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "histories"

    def __str__(self):
        return "User " + str(self.account.account_id)+ ": " + str(self.visit_datetime) + " " + str(self.site.url)


class Site(models.Model):
    name = models.CharField(max_length=50)
    account = models.ForeignKey("Account", on_delete=models.CASCADE, related_name="sites") #this collection of sites is the history

    url = models.URLField(max_length=2500)

    first_visit = models.DateTimeField(default=timezone.now) # need to put a method for this
    last_visit = models.DateTimeField(default=timezone.now) # need to put a method for this

    recent_frequency = models.IntegerField(default=0)  # number of visits in the last week #TODO need to write a method for this
    number_of_visits = models.IntegerField(default=1)  # keeps track of number of visits
    site_ranking = models.IntegerField(default=0) # uses a ranking algoithm to rank the sites

    # TODO Are these necessary?
    open_tab = models.BooleanField(verbose_name="Is this site opened in a tab?", default=True)
    bookmarked = models.BooleanField(verbose_name="Is this site bookmarked?", default = False)

    # TODO Add functionality once a site is visited (check the Tab class)
    def visited(self):
        self.last_visit = datetime.now()
        # site_ranking = # update site ranking here

    #TODO This needs to be implemented
    #Pseudocode for rankSite, a method that returns a number between 0 and 100, where the lower return value is the greater site ranking
    # def rankSite(self):
    #     if (self.number_of_visits > self.recent_frequency):
    #         return (self.recent_frequency/self.number_of_visits)*100
    #     else:
    #         return 0 #Should never get to this point, but if there are more reecent visits than total visits, this must be the highest ranked site

    def save(self, *args, **kwargs):
        # call super method to create Tab entry
        print("URL: ", )
        url1 = str(self.url).split('?')[0]
        url2 = url1.split('/')
        print("URL: ", url1 )
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
            history.save()
            
        except: # if site doesn't exist create it and create tab
            site = Site.objects.create(account = curr_account , url = site_url, 
                first_visit=first_visit, last_visit=last_visit)
            tab = Tab(account = curr_account, site = site, status = "open")
            history = History.objects.create(account=curr_account, site=site, visit_datetime=last_visit)
            history.save()

        if toSave:
            super(Tab, tab).save()
            
        return tab

    @classmethod
    def close_tab(cls, tabID, curr_account):
        try:
            # print("Models", tabID)
            tab = Tab.objects.filter(account = curr_account).get(id = tabID)

            tab.delete()
            return "successful"
        except:
            return "Tab doesn't exist for the current user"

    @classmethod
    def visit_tab(cls, tabID, curr_account):
        try:
            tab = Tab.objects.filter(account = curr_account).get(pk = tabID)[0]
            tab.last_visited = datetime.now()
            status = "active"
            tab.save()
            try:
                site = Site.objects.filter(account = curr_account).get(url = tab.url)[0]
            except:
                return "Site instance doesn't exist for the current user"
            return "successful"
        except:
            return "Tab instance doesn't exist for the current user"

    def __str__(self):
        return str(self.site.url)

    
    def save(self, *args, **kwargs):
        # call super method to create Tab entry
        account = Account.objects.filter(pk = self.account_id)[0]
        site =  Site.objects.filter(pk = self.site_id)[0]
        tab = Tab.open_tab(site.url, account, self.created_date, self.last_visited, toSave=False)
        super(Tab, self).save(*args, **kwargs)

        # create corresponding site object

class Bookmark(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="bookmarks")
    bookmark_name = models.CharField(verbose_name= "Bookmark name", max_length=50)
    created_date = models.DateTimeField(default=timezone.now) #keeps track of creation date
    site = models.OneToOneField(Site, on_delete=models.CASCADE) #if the site gets deleted the bookmark gets deleted
    last_visited = models.DateTimeField(default=timezone.now) #keeps track of last visited date
    recent_frequency = models.IntegerField(default=1) # number of visits in the last week
    number_of_visits = models.IntegerField(default=1)# keeps track of number of visits

    # TODO create a visited method
    #TODO create a method to calculate frequency

    def __str__(self):
        return str(self.bookmark_name)

    @classmethod
    def create_bookmark(cls, tab, curr_account, name='bookmark', last_visited=None):
        Bookmark.objects.create(account = curr_account, 
        bookmark_name = name, site=tab.site)

        print('bookmark created')
    
    @classmethod
    def delete_bookmark(cls, id):
        bookmark = Bookmark.objects.filter(pk=id).delete()
        print('bookmark deleted')


    

# TODO change bookmark status in the Site model on save
# Gerald: What is bookmark status?

# TODO need to make sure this deletes when account gets deleted (I think it does)
# TODO need to finalize the fields here
class Account_Preferences(models.Model):
    name = models.CharField(default="Account Preferences", max_length=10)
    home_page = models.OneToOneField(Site, on_delete=models.CASCADE, null= True, blank=True)

    # sync
    sync_enabled = models.BooleanField(default=True) # not sure if this is possible or useful
    # sharing
    searchable_profile = models.BooleanField(default=True)
    # security
    cookies_enabled = models.BooleanField(default=True)
    popups_enabled = models.BooleanField(default=True)
    # maybe split into device preferences too?
    # Misc
    #   home page

    # Display?
    #     Dark mode
    is_dark_mode = models.BooleanField(default=False)
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
    title = models.TextField(verbose_name="Shared Folder Title", max_length=100, default="sharedFolder")
    description = models.TextField(verbose_name="Shared Folder description")
    created_date = models.DateTimeField(default= timezone.now)
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="owner")

    # TODO need to have this be a many to many field
    collaborators = models.ManyToManyField(Account)
    #bookmarks = models.ManyToManyField(Bookmark)
    #tabs = models.ManyToManyField(Tab)
    #notes = models.ManyToManyField(Note)
    def __str__(self):
        return str(self.title)
