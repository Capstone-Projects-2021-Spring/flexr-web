from django.test import TestCase
from django.test import Client
from flexr_web.class_views.HistoryView import *
from flexr_web.models import *
from django.utils import timezone

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