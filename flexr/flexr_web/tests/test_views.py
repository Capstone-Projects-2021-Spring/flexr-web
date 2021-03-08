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


class AccountTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        c = Client()
        cls.curr_user = User.objects.create_user('foo', 'myemail@test.com', 'bar')
        cls.curr_user.save()
        cls.curr_user = authenticate(username='foo', password='bar')
        cls.acc = Account.objects.create(user = cls.curr_user, email = "test@me.com", type_of_account = "Business")

    def test_get_account(self):
        c = Client()
        c.login(username='foo', password='bar')
        result = c.get(path ="/api/account/1")
        #print('debug')
        #print(result.get('email'))
        #self.assertEqual(r.content, self.acc)


    def test_switch_account(self):
        pass

    def test_add_account(self):
        c = Client()
        c.login(username='foo', password='bar')
        extra = {
        'email': "email@site.com" ,
        'type_of_account': "Personal"
        }

        c.post(path="/api/account/", extra=extra)
        
        acc_count = Account.objects.all().count()

        self.assertEqual(acc_count, 2)


    def test_edit_account(self):
        pass

    def test_delete_account(self):
        c = Client()
        c.login(username='foo', password='bar')
        c.delete('/api/account/1')

        acc_count = Account.objects.all().count()

        self.assertEqual(acc_count, 0)