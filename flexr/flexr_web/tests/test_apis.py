from django.test import TestCase
from django.test import Client
from django.utils import timezone

#from flexr_web.class_views.HistoryView import *
from ..models import *

import datetime
import pytz
import json

class HistoryAPITestCase(TestCase):
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
        c.get(path='/switch_account/1')

        result = c.get(path ="/api/history/")
        data = json.loads(result.content)
        data_expected = [
            {'site': 1, 'account': 1, 'visit_datetime': '2020-04-20T00:00:00Z'}, 
            {'site': 2, 'account': 1, 'visit_datetime': '2020-04-21T00:00:00Z'}, 
            {'site': 3, 'account': 1, 'visit_datetime': '2020-04-22T00:00:00Z'}]

        self.assertEqual(data, data_expected)


    def test_filter_history(self):
        c = Client()
        c.login(username='foo', password='bar')
        c.get(path='/switch_account/1')


        payload = {
        'datetime_from' : datetime.datetime(year=2020, month=4, day=20, tzinfo=pytz.UTC),
        'datetime_to' : datetime.datetime(year=2020, month=4, day=21, tzinfo=pytz.UTC),
        }

        result = c.get(path ="/api/history/filter/", data=payload)
        data = json.loads(result.content)
        data_expected = [
            {'site': 1, 'account': 1, 'visit_datetime': '2020-04-20T00:00:00Z'}, 
            {'site': 2, 'account': 1, 'visit_datetime': '2020-04-21T00:00:00Z'}, 
            ]

        self.assertEqual(data, data_expected)

    def test_post_history_delete(self):
        c = Client()
        c.login(username='foo', password='bar')
        c.get(path='/switch_account/1')

        payload = {'DELETE': [1,3]}

        c.post(path ="/api/history/", data=payload)

        data = History.objects.all().count()
        data_expected = 1

        self.assertEqual(data, data_expected)

    def test_delete_history_range(self):
        c = Client()
        c.login(username='foo', password='bar')
        c.get(path='/switch_account/1')


        payload = json.dumps({
        'datetime_from' : 
        datetime.datetime(year=2020, month=4, day=21, tzinfo=pytz.UTC).isoformat(),

        'datetime_to' :
         datetime.datetime(year=2020, month=4, day=22, tzinfo=pytz.UTC).isoformat(),
        })

        c.delete(path ="/api/history/filter/", data=payload)

        data = History.objects.all().count()
        data_expected = 1

        self.assertEquals(data, data_expected)


    def test_delete_all_history(self):
        c = Client()
        c.login(username='foo', password='bar')
        c.get(path='/switch_account/1')
        c.delete(path ="/api/history/")
        


        data = History.objects.all().count()
        data_expected = 0

        self.assertEquals(data, data_expected)

class BookmarkAPITestCase(TestCase):
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

        for i, site in enumerate(sites):
            name = f'Bookmark {i+1}'
            Bookmark.objects.create(site=site, account=cls.acc, created_date=cls.now, last_visited=cls.now)


    def test_get_bookmark(self):
        c = Client()
        c.login(username='foo', password='bar')
        c.get(path='/switch_account/1')

        result = c.get(path ="/api/bookmarks/")
        data = json.loads(result.content)

        '''data_expected = {
            'account': 1,
            'bookmark_name': '',
            'created_date': '2020-04-20T00:00:00Z',
            'site': 1,
            'last_visited': '2020-04-20T00:00:00Z',
            'recent_frequency': 1,
            'number_of_visits': 1,

        }'''

        data_expected = len(data)

        self.assertEquals(3, data_expected)

    def test_add_bookmark(self):
        c = Client()
        c.login(username='foo', password='bar')
        c.get(path='/switch_account/1')

        site = Site.objects.create(account = self.acc, url = 'https://www.twitter.com')

        payload = {
            'site_id': site.id,
        }

        c.post(path='/api/bookmarks/', data=payload)

        bookmark_count = Bookmark.objects.all().count()
        bookmark = Bookmark.objects.all()[3]

        self.assertEqual(bookmark_count, 4)
        self.assertEqual(bookmark.site_id, payload['site_id'])
    


    def test_edit_bookmark(self):
        c = Client()
        c.login(username='foo', password='bar')
        c.get(path='/switch_account/1')

        site = Site.objects.create(account = self.acc, url = 'https://www.facebook.com')

        payload = json.dumps({
            'bookmark_name': 'bookmark',
            'site_id': site.id
            
        })

        c.put(path='/api/bookmarks/2', data=payload)
        

        bookmark = Bookmark.objects.get(pk = 2)

        self.assertEquals(bookmark.bookmark_name, 'bookmark')
        self.assertEquals(bookmark.site_id, site.id)



    def test_del_bookmark(self):
        c = Client()
        c.login(username='foo', password='bar')
        c.get(path='/switch_account/1')
        c.delete(path ="/api/bookmarks/1")

        data = Bookmark.objects.all().count()
        data_expected = 2

        self.assertEquals(data, data_expected)

    def test_del_all_bookmarks(self):
        c = Client()
        c.login(username='foo', password='bar')
        c.get(path='/switch_account/1')
        c.delete(path ="/api/bookmarks/all")

        data = Bookmark.objects.all().count()
        data_expected = 0

        self.assertEquals(data, data_expected)


class UserAPITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.curr_user = User.objects.create_user('foo', 'myemail@test.com', 'bar')
        cls.curr_user.save()
        

    def test_sign_up(self):
        c = Client()

        payload = {
        "username": "username",
        "email": "email@domain.com",
        "password": "password"
        }

        result = c.post(path='/api/register/', data=payload)

        data = User.objects.all().count()
        data_expected = 2

        self.assertEquals(data, data_expected)

        

    def test_login(self):
        c = Client()

        payload = {
        "username": "foo",
        "password": "bar"
        }

        result = c.post(path='/api/login/', data=payload)
        data = json.loads(result.content)
        print(data)

        self.assertEquals(result.status_code, 200)

    def test_logout(self):
        c = Client()
        c.login(username='foo', password='bar')

        result = c.get(path='/api/logout/')

        self.assertEquals(result.status_code, 200)


    def test_check_status(self):
        c = Client()

        result = c.get(path='/api/status/')
        data = json.loads(result.content)
        self.assertEquals(data, False)

        c.login(username='foo', password='bar')
        result = c.get(path='/api/status/')
        data = json.loads(result.content)
        self.assertEquals(data, True)