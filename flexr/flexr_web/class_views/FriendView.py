from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView

import pytz

from ..models import *
from ..forms import *

class FriendView(LoginRequiredMixin, DetailView):

    def get(self, request):
        curr_account = request.user.accounts.get(account_id=request.session['account_id'])
        friends = curr_account.friends.all()
        print(friends)
        return render(request, "flexr_web/friends.html", {"Friends": friends})

    def add_friend(self, request):
        friend_acc_id = request.POST.get('account_friend')
        friend_account = Account.objects.get(account_id=friend_acc_id)
        user_account = request.user.accounts.get(account_id=request.session['account_id'])
        friend_request = Friendship.objects.get_or_create(sent=user_account, received=friend_account)
        return redirect('/friends')

    def deny_friend(self, request, pk):
        friend_request = Friendship.objects.get(id=pk)
        friend_request.status = "Declined"
        friend_request.save()
        request.session['message'] = "Friend request DENIED"
        return redirect('/profile')

    def accept_friend(self, request, pk):
        friend_request = Friendship.objects.get(id=pk)
        friend_request.status = "Accepted"
        friend_request.save()
        request.session['message'] = "Friend request ACCEPTED"
        return redirect('/profile')

    def remove_notif(self, request, pk):
        curr_account = request.user.accounts.get(account_id=request.session['account_id'])
        notif = curr_account.notifs.get(id=pk)
        curr_account.notifs.remove(notif)
        curr_account.save()
        return redirect('/')

    def remove_friend(self, request, pk):
        current_account = request.user.accounts.get(account_id=request.session['account_id'])
        friend_account = Account.objects.get(account_id=pk)

        current_account.all_friends.remove(friend_account)
        friend_account.all_friends.remove(current_account)
        friendship = Friendship.objects.filter(sent=current_account, received=friend_account)
        if (friendship.count() == 0):
            friendship = Friendship.objects.filter(sent=friend_account, received=current_account)
            if (friendship.count() == 0):
                request.session['errmessage'] = "Trouble finding friendship"
                return redirect('/profile')
        friendship = friendship[0]
        friendship.status = "Declined"
        friendship.save()
        current_account.save()
        friend_account.save()
        request.session['message'] = "Friend deleted"
        return redirect('/profile')