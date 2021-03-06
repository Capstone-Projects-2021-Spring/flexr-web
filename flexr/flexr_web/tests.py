from django.test import TestCase
from .models import *
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
        test_site = Site.objects.create(account = test_acc, url = "www.google.com")
        test_site.save()

    def test_site_created(self):
        test_acc = Account.objects.get(email = "anon@gmail.com")
        site_count = test_acc.sites.all().count()
        self.assertEqual(site_count, 1)

    def test_create_another_site(self):
        test_acc = Account.objects.get(email = "anon@gmail.com")
        site2 = Site.objects.create(account = test_acc, url = "www.facebook.com")
        site2.save()
        site_count = test_acc.sites.all().count()
        self.assertEqual(site_count, 2)

    def test_delete_site(self):
        test_acc = Account.objects.get(email="anon@gmail.com")
        site2 = Site.objects.get(url = "www.google.com")
        site_count = test_acc.sites.all().count()
        self.assertEqual(site_count, 1)

    def test_update_recent_frequency(self):
        site2 = Site.objects.get(url="www.google.com")
        site2.number_of_visits += 1
        site2.save()
        self.assertEqual(site2.number_of_visits, 2)

    # Need to create a test for the site ranking field

    # need to create a test for the datetimefields

class DeviceTestCase(TestCase):

    def setUp(self):
        test_user = User.objects.create(first_name = "Al", last_name = "Annon", username="annon1234", email = "anon@gmail.com")
        test_user.save()
        test_acc = Account.objects.create(user=test_user, email=test_user.email, phone_number="5704600704",
                                          type_of_account="Business")
        test_acc.save()
        test_device = Device.objects.create(account=test_acc, name="Test Device")
        test_device.save()

    def test_device_created(self):
        test_acc = Account.objects.get(email="anon@gmail.com")
        device_count = test_acc.devices.all().count()
        self.assertEqual(device_count, 1, "Device count is 1")

    def test_create_another_device(self):
        test_acc = Account.objects.get(email="anon@gmail.com")
        test_device2 = Device.objects.create(account=test_acc, name="Test Device 2")
        test_device2.save()
        device_count = test_acc.devices.all().count()
        self.assertEqual(device_count, 2, "Device count is 2")

    def test_device_edit(self):
        test_device = Device.objects.get(name = "Test Device")
        test_device.name = "Bob's Device"
        test_device.save()
        self.assertEqual(test_device.name, "Bob's Device")

    def test_device_deleted(self):
        test_device = Device.objects.get(name = "Test Device")
        test_device.delete()
        test_device.save()
        test_acc = Account.objects.get(email="anon@gmail.com")
        device_count = test_acc.devices.all().count()
        self.assertEqual(device_count, 1, "Device count is 1")

class BookmarkTestCase(TestCase):

    def setUp(self):
        test_user = User.objects.create(first_name = "Al", last_name = "Annon", username="annon1234", email = "anon@gmail.com")
        test_user.save()
        test_acc = Account.objects.create(user=test_user, email=test_user.email, phone_number="5704600704",
                                          type_of_account="Business")
        test_acc.save()
        test_site = Site.objects.create(account = test_acc, url = "www.google.com")
        test_site.save()
        test_bookmark = Bookmark.objects.create(account = test_acc, bookmark_name = "Google", site = test_site)
        test_bookmark.save()

    def test_bookmark_created(self):
        test_acc = Account.objects.get(email="anon@gmail.com")
        bookmark_count = test_acc.bookmarks.all().count()
        self.assertEqual(bookmark_count, 1, "Bookmark count is 1")

    def test_create_another_bookmark(self):
        test_acc = Account.objects.get(email="anon@gmail.com")
        test_site2 = Site.objects.create(account=test_acc, url="www.reddit.com")
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
        test_site = Site.objects.create(account = test_acc, url = "www.google.com")
        test_site.save()
        test_tab = Tab.objects.create(account = test_acc, site = test_site)
        test_tab.save()

    def test_tab_created(self):
        test_acc = Account.objects.get(email="anon@gmail.com")
        tab_count = test_acc.tabs.all().count()
        self.assertEqual(tab_count, 1, "Tab count is 1")

    def test_create_another_tab(self):
        test_acc = Account.objects.get(email="anon@gmail.com")
        test_site2 = Site.objects.create(account=test_acc, url="www.reddit.com")
        test_site2.save()
        test_tab2 = Tab.objects.create(account=test_acc, site=test_site2)
        test_tab2.save()
        tab_count = test_acc.tabs.all().count()
        self.assertEqual(tab_count, 2, "Tab count is 2")

    def test_tab_deleted(self):
        test_acc = Account.objects.get(email="anon@gmail.com")
        test_site = Site.objects.get(url="www.google.com")
        test_tab = Tab.objects.get(site = test_site)
        test_tab.delete()
        test_tab.save()
        tab_count = test_acc.tabs.all().count()
        self.assertEqual(tab_count, 1, "Tab count is 1")