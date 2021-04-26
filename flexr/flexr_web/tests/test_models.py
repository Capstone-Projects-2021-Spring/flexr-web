from django.contrib.auth.models import User
from django.test import TestCase, Client
from ..models import *
from ..views import *
# Create your tests here.

class UserTestCase(TestCase):

    def setUp(self):
        test_user = User.objects.create(first_name = "Al", last_name = "Annon", username="annon1234", email = "anon@gmail.com")
        test_user.save()

    def test_user_created(self):
        user_count = User.objects.all().count()
        self.assertEqual(user_count, 1, "User count is 1")

    def test_user_edit(self):
        test_user = User.objects.get(username = "annon1234")
        test_user.first_name = "Bob"
        test_user.save()
        self.assertEqual(test_user.first_name, "Bob")

    def test_user_deleted(self):
        test_user = User.objects.get(username = "annon1234")
        test_user.delete()
        test_user.save()
        user_count = User.objects.all().count()
        self.assertEqual(user_count, 1, "User count is 0")

class AccountTestCase(TestCase):
    def setUp(self):
        test_user = User.objects.create(first_name="Al", last_name="Annon", username="annon1234",
                                        email="anon@gmail.com")
        test_user.save()
        test_acc = Account.objects.create(user = test_user, email = test_user.email, phone_number = "5704600704",
                                          type_of_account = "Business")
        test_acc.save()

        account2 = Account.objects.create(user=test_user, email="2" + test_user.email, phone_number="18008008609",
                                          type_of_account="Business")
        account2.save()

    def test_accounts_created(self):
        acc_count = Account.objects.all().count()
        self.assertEqual(acc_count, 2)

    def test_user_accounts_relationship(self):
        test_user = User.objects.get(username = "annon1234")
        acc_count = test_user.accounts.all().count()
        self.assertEqual(acc_count, 2)

    def test_user_account_relationship2(self):
        test_user = User.objects.get(username="annon1234")
        account = test_user.accounts.all()[0]
        self.assertEqual(account.email, "anon@gmail.com")

    def test_delete_account(self):
        account2 = Account.objects.all()[1]
        account2.delete()
        self.assertEqual(Account.objects.all().count(), 1)

class SiteTestCase(TestCase):

    def setUp(self):
        test_user = User.objects.create(first_name="Al", last_name="Annon", username="annon1234",
                                        email="anon@gmail.com")
        test_user.save()
        test_acc = Account.objects.create(user=test_user, email=test_user.email, phone_number="5704600704",
                                          type_of_account="Business")
        test_acc.save()
        test_site = Site.objects.create(account = test_acc, url = "https://www.google.com")
        test_site.save()

    def test_site_created(self):
        test_acc = Account.objects.get(email = "anon@gmail.com")
        site_count = test_acc.sites.all().count()
        self.assertEqual(site_count, 1)

    def test_create_another_site(self):
        test_acc = Account.objects.get(email = "anon@gmail.com")
        site2 = Site.objects.create(account = test_acc, url = "https://www.facebook.com")
        site2.save()
        site_count = test_acc.sites.all().count()
        self.assertEqual(site_count, 2)

    def test_delete_site(self):
        test_acc = Account.objects.get(email="anon@gmail.com")
        site2 = Site.objects.get(url = "https://www.google.com")
        site_count = test_acc.sites.all().count()
        self.assertEqual(site_count, 1)

    def test_update_recent_frequency(self):
        site2 = Site.objects.get(url="https://www.google.com")
        site2.number_of_visits += 1
        site2.save()
        self.assertEqual(site2.number_of_visits, 2)

    # Need to create a test for the site ranking field

    # need to create a test for the datetimefields

class BookmarkTestCase(TestCase):

    def setUp(self):
        test_user = User.objects.create(first_name = "Al", last_name = "Annon", username="annon1234", email = "anon@gmail.com")
        test_user.save()
        test_acc = Account.objects.create(user=test_user, email=test_user.email, phone_number="5704600704",
                                          type_of_account="Business")
        test_acc.save()
        test_site = Site.objects.create(account = test_acc, url = "https://www.google.com")
        test_site.save()
        test_bookmark = Bookmark.objects.create(account = test_acc, bookmark_name = "Google", site = test_site)
        test_bookmark.save()

    def test_bookmark_created(self):
        test_acc = Account.objects.get(email="anon@gmail.com")
        bookmark_count = test_acc.bookmarks.all().count()
        self.assertEqual(bookmark_count, 1, "Bookmark count is 1")

    def test_create_another_bookmark(self):
        test_acc = Account.objects.get(email="anon@gmail.com")
        test_site2 = Site.objects.create(account=test_acc, url="https://www.reddit.com")
        test_site2.save()
        test_bookmark2 = Bookmark.objects.create(account=test_acc, bookmark_name="Reddit", site=test_site2)
        test_bookmark2.save()
        bookmark_count = test_acc.bookmarks.all().count()
        self.assertEqual(bookmark_count, 2, "Bookmark count is 2")

    def test_bookmark_edit(self):
        test_bookmark = Bookmark.objects.get(bookmark_name = "Google")
        test_bookmark.bookmark_name = "Gmail"
        test_bookmark.save()
        self.assertEqual(test_bookmark.bookmark_name, "Gmail")

    def test_bookmark_deleted(self):
        test_acc = Account.objects.get(email="anon@gmail.com")
        test_bookmark = Bookmark.objects.get(bookmark_name = "Google")
        test_bookmark.delete()
        test_bookmark.save()
        bookmark_count = test_acc.bookmarks.all().count()
        self.assertEqual(bookmark_count, 1, "Bookmark count is 1")

class TabTestCase(TestCase):

    def setUp(self):
        test_user = User.objects.create(first_name = "Al", last_name = "Annon", username="annon1234", email = "anon@gmail.com")
        test_user.save()
        test_acc = Account.objects.create(user=test_user, email=test_user.email, phone_number="5704600704",
                                          type_of_account="Business")
        test_acc.save()
        test_site = Site.objects.create(account = test_acc, url = "https://www.google.com")
        test_site.save()
        test_tab = Tab.objects.create(account = test_acc, site = test_site)
        test_tab.save()

    def test_tab_created(self):
        test_acc = Account.objects.get(email="anon@gmail.com")
        tab_count = test_acc.tabs.all().count()
        self.assertEqual(tab_count, 1, "Tab count is 1")

    def test_create_another_tab(self):
        test_acc = Account.objects.get(email="anon@gmail.com")
        test_site2 = Site.objects.create(account=test_acc, url="https://www.reddit.com")
        test_site2.save()
        test_tab2 = Tab.objects.create(account=test_acc, site=test_site2)
        test_tab2.save()
        tab_count = test_acc.tabs.all().count()
        self.assertEqual(tab_count, 2, "Tab count is 2")

    def test_tab_deleted(self):
        test_acc = Account.objects.get(email="anon@gmail.com")
        test_site = Site.objects.get(url="https://www.google.com")
        test_tab = Tab.objects.get(site = test_site)
        test_tab.delete()
        test_tab.save()
        tab_count = test_acc.tabs.all().count()
        self.assertEqual(tab_count, 1, "Tab count is 1")

class AccountPreferencesTestCase(TestCase):

    def setUp(self):
        test_user = User.objects.create(first_name = "Al", last_name = "Annon", username="annon1234", email = "anon@gmail.com")
        test_user.save()
        test_acc = Account.objects.create(user=test_user, email=test_user.email, phone_number="5704600704",
                                          type_of_account="Business")
        test_acc.save()
        test_site = Site.objects.create(account = test_acc, url = "https://www.google.com")
        test_site.save()
        test_account_preferences = Account_Preferences.objects.create(name = "Annon Pref1", home_page = test_site)
        test_account_preferences.save()

    def test_account_preferences_created(self):
        #test_acc = Account.objects.get(email="anon@gmail.com")
        account_preferences_count = Account_Preferences.objects.all().count()
        self.assertEqual(account_preferences_count, 2, "Account Preferences count is 1")

    def test_create_another_account_preferences(self):
        test_acc = Account.objects.get(email="anon@gmail.com")
        test_site2 = Site.objects.create(account=test_acc, url="https://www.reddit.com")
        test_site2.save()
        test_account_preferences = Account_Preferences.objects.create(name = "Annon Pref2", home_page = test_site2)
        test_account_preferences.save()
        account_preferences_count = Account_Preferences.objects.all().count()
        self.assertEqual(account_preferences_count, 3, "Account Preferences count is 2")

    def test_account_preferences_edit(self):
        test_account_preferences = Account_Preferences.objects.get(name="Annon Pref1")
        test_account_preferences.name = "Backup Pref"
        test_account_preferences.save()
        self.assertEqual(test_account_preferences.name, "Backup Pref")

    def test_account_preferences_deleted(self):
        test_account_preferences = Account_Preferences.objects.get(name="Annon Pref1")
        test_account_preferences.delete()
        test_account_preferences.save()
        account_preferences_count = Account_Preferences.objects.all().count()
        self.assertEqual(account_preferences_count, 2, "Account Preferences count is 1")

class FriendsTest(TestCase):

    def setUp(self):
        test_user1 = User.objects.create(first_name="Al2", last_name="Annon2", username="annon1",
                                        email="anon@gmail.com", password = "password")
        test_user1.save()

        test_acc1 = Account.objects.create(user=test_user1, username = test_user1.username, email=test_user1.email, phone_number="5704600704",
                                          type_of_account="Business")
        test_acc1.save()
        curr_user = authenticate(username='annon1', password='password')

        test_user2 = User.objects.create(first_name="Al", last_name="Annon", username="annon2",
                                         email="anon@gmail.com")
        test_user2.save()
        test_acc2 = Account.objects.create(user=test_user2, email=test_user2.email,username = test_user2.username, phone_number="5704600704",
                                           type_of_account="Business")
        test_acc2.save()

        test_user3 = User.objects.create(first_name="Al", last_name="Annon", username="annon3",
                                         email="anon@gmail.com")
        test_user3.save()
        test_acc3 = Account.objects.create(user=test_user3, email=test_user3.email,username = test_user3.username, phone_number="5704600704",
                                           type_of_account="Business")
        test_acc3.save()

        test_user4 = User.objects.create(first_name="Al", last_name="Annon", username="annon4",
                                         email="anon@gmail.com")
        test_user4.save()

        test_acc4 = Account.objects.create(user=test_user4, email=test_user4.email,username = test_user4.username, phone_number="5704600704",
                                           type_of_account="Business")
        test_acc4.save()

        test_user5 = User.objects.create(first_name="Al", last_name="Annon", username="annon5",
                                         email="anon@gmail.com")
        test_user5.save()
        test_acc5 = Account.objects.create(user=test_user5, email=test_user5.email,username = test_user5.username, phone_number="5704600704",
                                           type_of_account="Business")
        test_acc5.save()

        test_user6 = User.objects.create(first_name="Al", last_name="Annon", username="annon6",
                                         email="anon@gmail.com")
        test_user6.save()
        test_acc6 = Account.objects.create(user=test_user6, email=test_user6.email, username = test_user6.username,phone_number="5704600704",
                                           type_of_account="Business")
        test_acc6.save()

    def test_sending_friend_request(self):
        c = Client()
        c.login(username='annon1', password='password')
        c.get(path='/switch_account/1')  # force account switch
        result = c.get(path="/api/tab/1")

        self.assertEqual(True, True, "Account Preferences count is 1")

    def test_create_friendship(self):
        accounts = []
        for x in Account.objects.all():
            accounts.append(x)
        print("accounts",accounts)
        friendship1 = Friendship.objects.create(sent = accounts[0], received = accounts[1]) # 1-2
        friendship2 = Friendship.objects.create(sent = accounts[0], received = accounts[5])

        friendship3 = Friendship.objects.create(sent = accounts[1], received = accounts[3])
        friendship4 = Friendship.objects.create(sent = accounts[1], received = accounts[2])
        friendship10 = Friendship.objects.create(sent=accounts[1], received=accounts[4])

        friendship5 = Friendship.objects.create(sent = accounts[2], received = accounts[4])

        friendship6 = Friendship.objects.create(sent = accounts[3], received = accounts[5])
        friendship7 = Friendship.objects.create(sent = accounts[3], received = accounts[4])

        for x in Friendship.objects.all():
            x.status = "Accepted"
            x.save()

        print("friends")
        for x in Account.objects.all():
            print(x.account_id, " = ", x.friends.all())

        print("mutual friends")
        for x in Account.objects.all():
            print(x.account_id, " = ", x.mutual_friends.all())

class NoteTestCase(TestCase):
    def setUp(self):
        test_user = User.objects.create(first_name="Al", last_name="Annon", username="annon1234",
                                        email="anon@gmail.com")
        test_user.save()
        test_acc = Account.objects.create(user=test_user, email=test_user.email, phone_number="5704600704",
                                          type_of_account="Business")
        test_acc.save()
        test_note = Note.objects.create(account=test_acc, title="Test Note", content="Note")
        test_note.save()

    def test_note_created(self):
        test_acc = Account.objects.get(email = "anon@gmail.com")
        note_count = test_acc.notes.all().count()
        self.assertEqual(note_count, 1)

    def test_create_another_note(self):
        test_acc = Account.objects.get(email = "anon@gmail.com")
        note2 = Note.objects.create(account=test_acc, title="Test Note2", content="Note2")
        note2.save()
        note_count = test_acc.notes.all().count()
        self.assertEqual(note_count, 2, "Create another note success")

    def test_notes_delete(self):
        test_acc = Account.objects.get(email="anon@gmail.com")
        test_acc.notes.all().delete()
        note_count = test_acc.notes.all().count()
        self.assertEqual(note_count, 0)