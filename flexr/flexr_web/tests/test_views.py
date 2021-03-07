from django.test import TestCase
from django.test import Client
from flexr_web.views import *
from flexr_web.models import *

class TabTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        c = Client()
        curr_user = User.objects.create_user('foo', 'myemail@test.com', 'bar')
        curr_user.save()
        curr_user = authenticate(username='foo', password='bar')
        acc = Account.objects.create(user = curr_user, email = "test@me.com", type_of_account = "Business")
        site = Site.objects.create(account = acc, url = "www.google.com")
        tab = Tab.objects.create(account = acc, site = site, status = "Open")

    def test_get_tab(self):
        c = Client()
        c.login(username='foo', password='bar')
        c.get(path ="/api/tab/1")

    def test_delete_tab(self):
        c = Client()
        c.login(username='foo', password='bar')
        c.delete(path = "/api/tab/1")
        tab_count = Tab.objects.all().count()
        self.assertEqual(tab_count, 0)

    def test_open_tab(self):
        c = Client()
        c.login(username='foo', password='bar')
        c.post("/api/tab/-1", {"url": "www.facebook.com"})
        tab_count = Tab.objects.all().count()
        self.assertEqual(tab_count, 2)
