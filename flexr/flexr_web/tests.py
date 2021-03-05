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
