from django.test import TestCase
from django.test import Client
from ..views import *
from ..models import *
from django.utils import timezone

import datetime
import pytz
import json

class TabTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        c = Client()
        curr_user = User.objects.create_user('foo', 'myemail@test.com', 'bar')
        curr_user.save()
        curr_user = authenticate(username='foo', password='bar')
        cls.now = datetime.datetime.now(tz=timezone.utc)
        acc = Account.objects.create(user = curr_user, email = "test@me.com", type_of_account = "Business")
        site = Site.objects.create(account = acc, url = "https://www.google.com/")
        tab = Tab.objects.create(account = acc, site = site, status = "Open", 
            created_date = cls.now, last_visited = cls.now)


    def test_get_tab(self):
        c = Client()
        c.login(username='foo', password='bar')
        c.get(path='/switch_account/1') # force account switch
        result = c.get(path ="/api/tab/1")
        data = json.loads(result.content)
        
        # remove timezone and then append 'Z' to match format
        # hack to remove warning
        data_expected = {
            'account': 1, 
            'site': 1, 
            'created_date': self.now.isoformat()[:-6] + 'Z', 
            'last_visited': self.now.isoformat()[:-6] + 'Z', 
            'status': 'Open'
        }

        self.assertEqual(data, data_expected)

    def test_delete_tab(self):
        c = Client()
        c.login(username='foo', password='bar')
        c.get(path='/switch_account/1') # force account switch
        c.delete(path = "/api/tab/1")
        tab_count = Tab.objects.all().count()
        self.assertEqual(tab_count, 0)

    def test_open_tab(self):
        c = Client()
        c.login(username='foo', password='bar')
        c.get(path='/switch_account/1') # force account switch
        c.post("/api/tab/-1", {"url": "https://www.facebook.com"})
        tab_count = Tab.objects.all().count()
        self.assertEqual(tab_count, 2)


class AccountTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.curr_user = User.objects.create_user('foo', 'myemail@test.com', 'bar')
        cls.curr_user.save()
        cls.now = datetime.datetime.now(tz=timezone.utc)

        cls.acc = Account.objects.create(user = cls.curr_user, email = "test@me.com",
         type_of_account = "Business", date_joined=cls.now)


    def test_get_account(self):
        c = Client()
        c.login(username='foo', password='bar')
        result = c.get(path ="/api/account/1")
        data = json.loads(result.content)

        # remove timezone and then append 'Z' to match format
        # hack to remove warning
        data_expected = {
            'user': 1,
            'email': 'test@me.com',
            'type_of_account': 'Business',
            'date_joined': self.now.isoformat()[:-6] + 'Z', 
            'account_id': 1,
            'phone_number': '',
            'account_preferences': 1
        }

 
        # check that all fields are equal
        # simply checking equality on models only checks primary keys
        self.assertEqual(data, data_expected)

    def test_get_account_404(self):
        c = Client()
        c.login(username='foo', password='bar')
        result = c.get(path ="/api/account/3") # out of range

        #
        data = result.status_code
        data_expected = 404
        
        self.assertEquals(data, data_expected)

    def test_switch_account(self):
        c = Client()
        c.login(username='foo', password='bar')

        Account.objects.create(user = self.curr_user, email = "email@site.com", 
        type_of_account = "Personal")

        result = c.patch(path="/api/account/2")
        data = result.status_code
        data_expected = 200
        

        self.assertEqual(data, data_expected)

    def test_switch_account_404(self):
        c = Client()
        c.login(username='foo', password='bar')

        Account.objects.create(user = self.curr_user, email = "email@site.com", 
        type_of_account = "Personal")

        result = c.patch(path="/api/account/1337") #out of range
        data = result.status_code
        data_expected = 404
        

        self.assertEqual(data, data_expected)

    def test_add_account(self):
        c = Client()
        c.login(username='foo', password='bar')

        payload = {
        'email': "email@site.com" ,
        'type_of_account': "Personal"
        }
        result = c.post(path="/api/account/", data=payload)
        
        acc_count = Account.objects.all().count()
        acc = Account.objects.all()[1]

        self.assertEqual(acc_count, 2)
        self.assertEqual(acc.email, "email@site.com")
        self.assertEqual(acc.type_of_account, "Personal")


    def test_edit_account(self):
        c = Client()
        c.login(username='foo', password='bar')
        payload = json.dumps({
        "email": "email@site.com" ,
        "type_of_account": "Personal"
        })

        c.put(path="/api/account/1", data=payload)

        acc = Account.objects.get(pk = 1)

        self.assertEqual(acc.email, "email@site.com")
        self.assertEqual(acc.type_of_account, "Personal")

    def test_delete_account(self):
        c = Client()
        c.login(username='foo', password='bar')
        c.delete('/api/account/1')

        acc_count = Account.objects.all().count()

        self.assertEqual(acc_count, 0)

class HistoryTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.curr_user = User.objects.create_user('foo', 'myemail@test.com', 'bar')
        cls.curr_user.save()
        cls.now = datetime.datetime(year=2020, month=4, day=20, tzinfo=pytz.UTC)

        cls.acc = Account.objects.create(user = cls.curr_user, email = "test@me.com",
         type_of_account = "Business", date_joined = cls.now)

        sites = [
            Site.objects.create(account = cls.acc, url = 'https://www.google.com'),
            Site.objects.create(account = cls.acc, url = 'https://www.chess.com'),
            Site.objects.create(account = cls.acc, url = 'https://www.youtube.com'),
        ]

        for i,site in enumerate(sites):
            delta = datetime.timedelta(days=i)
            History.objects.create(site=site, account=cls.acc, visit_datetime=cls.now + delta)


    def test_get_history(self):
        c = Client()
        c.login(username='foo', password='bar')
        result = c.get(path ="/api/history/1")
        data = json.loads(result.content)
        data_expected = [
            {'site': 1, 'account': 1, 'visit_datetime': '2020-04-20T00:00:00Z'}, 
            {'site': 2, 'account': 1, 'visit_datetime': '2020-04-21T00:00:00Z'}, 
            {'site': 3, 'account': 1, 'visit_datetime': '2020-04-22T00:00:00Z'}]

        self.assertEqual(data, data_expected)


    def test_filter_history(self):
        c = Client()
        c.login(username='foo', password='bar')

        payload = {
        'datetime_from' : datetime.datetime(year=2020, month=4, day=20, tzinfo=pytz.UTC),
        'datetime_to' : datetime.datetime(year=2020, month=4, day=21, tzinfo=pytz.UTC),
        }

        result = c.get(path ="/api/history/1/filter", data=payload)
        data = json.loads(result.content)
        data_expected = [
            {'site': 1, 'account': 1, 'visit_datetime': '2020-04-20T00:00:00Z'}, 
            {'site': 2, 'account': 1, 'visit_datetime': '2020-04-21T00:00:00Z'}, 
            ]

        self.assertEqual(data, data_expected)

    def test_delete_history_range(self):
        c = Client()
        c.login(username='foo', password='bar')

        payload = json.dumps({
        'datetime_from' : 
        datetime.datetime(year=2020, month=4, day=21, tzinfo=pytz.UTC).isoformat(),

        'datetime_to' :
         datetime.datetime(year=2020, month=4, day=22, tzinfo=pytz.UTC).isoformat(),
        })

        c.delete(path ="/api/history/1/filter", data=payload)

        data = History.objects.all().count()
        data_expected = 1

        self.assertEquals(data, data_expected)


    def test_delete_all_history(self):
        c = Client()
        c.login(username='foo', password='bar')
        c.delete(path ="/api/history/1")

        data = History.objects.all().count()
        data_expected = 0

        self.assertEquals(data, data_expected)

def AccountPreferencesTestCase(TestCase):
    def setUp(self):
        test_user = User.objects.create(first_name="Al", last_name="Annon", username="annon1234",
                                        email="anon@gmail.com", password = "password")
        test_user.save()
        test_acc = Account.objects.create(user=test_user, email=test_user.email, phone_number="5704600704",
                                          type_of_account="Business")
        test_acc.save()
        test_site = Site.objects.create(account=test_acc, url="https://www.google.com")
        test_site.save()
        test_account_preferences = Account_Preferences.objects.create(name="Annon Pref1", home_page=test_site)
        test_account_preferences.save()

    def test_account_preferences_created(self):
        # test_acc = Account.objects.get(email="anon@gmail.com")
        account_preferences_count = Account_Preferences.objects.all().count()
        self.assertEqual(account_preferences_count, 2, "Account Preferences count is 1")

    def test_account_preferences_edit(self):
        c = Client()
        c.login(username='annon1234', password='password')
        payload = {
            'datetime_from': datetime.datetime(year=2020, month=4, day=20, tzinfo=pytz.UTC),
            'datetime_to': datetime.datetime(year=2020, month=4, day=21, tzinfo=pytz.UTC),
        }
        test_site = Site.objects.get(url = "https://www.google.com")
        result = c.get(path="/api/account_preferences/")
        data = json.loads(result.content)
        data_expected = [
            {'home_page': test_site, 'home_page_url': test_site.url}
        ]

        self.assertEqual(data, data_expected, "Account Preferences works")

def NoteTestCase(TestCase):
    def setUp(self):
        test_user = User.objects.create(first_name="Al", last_name="Annon", username="annon1234",
                                        email="anon@gmail.com", password = "password")
        test_user.save()
        test_acc = Account.objects.create(user=test_user, email=test_user.email, phone_number="5704600704",
                                          type_of_account="Business")
        test_acc.save()
        test_note = Note.objects.create(account=test_acc, title="Test Note", content="Note")
        test_note.save()

    def testNoteCreated(self):
        note_count = Note.objects.all().count()
        self.assertEqual(note_count, 2, "Notes count is 1")