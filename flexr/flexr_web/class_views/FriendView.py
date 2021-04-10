from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView

import pytz

from ..models import *
from ..forms import *
from ..serializers import AccountSerializer, FriendshipSerializer


class FriendView(LoginRequiredMixin, DetailView):

    def get(self, request):
        curr_account = request.user.accounts.get(account_id=request.session['account_id'])
        friends = curr_account.friends.all()
        print(friends)
        request.session['prev_url'] = '/friends/'
        return render(request, "flexr_web/friends.html", {"Friends": friends})

    def add_friend(self, request):
        friend_acc_id = request.POST.get('account_friend')
        print("FriendView: add_friend : friend_acc_id",friend_acc_id)
        friend_account = Account.objects.get(account_id=friend_acc_id)
        user_account = request.user.accounts.get(account_id=request.session['account_id'])
        friend_request = Friendship.objects.get_or_create(sent=user_account, received=friend_account)
        print(friend_request)
        request.session['message'] = "Friend request sent"
        return redirect(request.session['prev_url'])

    def deny_friend(self, request, pk):
        friend_request = Friendship.objects.get(id=pk)
        friend_request.status = "Declined"
        friend_request.save()
        request.session['message'] = "Friend request denied"
        return redirect(request.session['prev_url'])

    def accept_friend(self, request, pk):
        friend_request = Friendship.objects.get(id=pk)
        friend_request.status = "Accepted"
        friend_request.save()
        request.session['message'] = "Friend request accepted"
        return redirect(request.session['prev_url'])

    def remove_notif(self, request, pk):
        curr_account = request.user.accounts.get(account_id=request.session['account_id'])
        notif = curr_account.notifs.get(id=pk)
        curr_account.notifs.remove(notif)
        curr_account.save()
        return redirect(request.session['prev_url'])

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
                return redirect(request.session['prev_url'])
        friendship = friendship[0]
        friendship.status = "Declined"
        friendship.save()
        current_account.save()
        friend_account.save()
        request.session['message'] = "Friend deleted"
        return redirect(request.session['prev_url'])

@method_decorator(csrf_exempt, name='dispatch')
class FriendAPIView(LoginRequiredMixin, DetailView):
    def get(self, request):
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
        # friends = curr_account.friends.all()
        friendships_sent = curr_account.from_friend.all()
        friendships_recieved = curr_account.to_friend.all()
        # this merges two sets
        friendships = friendships_sent | friendships_recieved
        data = FriendshipSerializer(friendships, many=True)
        return JsonResponse(data.data, safe=False)

    def delete(self, request, *args, **kwargs):
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
        friendships_sent = curr_account.from_friend.all()
        friendships_recieved = curr_account.to_friend.all()
        friendships = friendships_sent | friendships_recieved
        friendship = friendships.get(id = kwargs['id'])

        if(friendship.sent is not curr_account):
            curr_account.all_friends.remove(friendship.sent)
            friendship.sent.all_friends.remove(curr_account)
        else:
            curr_account.all_friends.remove(friendship.received)
            friendship.received.all_friends.remove(curr_account)
        friendship.status = "Declined"
        friendship.save()
        data = FriendshipSerializer(friendships)
        return JsonResponse(data.data, safe=False)

    @method_decorator(csrf_exempt)
    def accept(self, request, *args, **kwargs):
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
        friendships_sent = curr_account.from_friend.all()
        friendships_recieved = curr_account.to_friend.all()
        friendships = friendships_sent | friendships_recieved
        friendship = friendships.get(id = kwargs['id'])
        print(friendship)
        friendship.status = "Accepted"
        friendship.save()
        data = FriendshipSerializer(friendships)
        return JsonResponse(data.data, safe=False)

    @method_decorator(csrf_exempt)
    def deny(self, request, *args, **kwargs):
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
        friendships_sent = curr_account.from_friend.all()
        friendships_recieved = curr_account.to_friend.all()
        friendships = friendships_sent | friendships_recieved
        friendship = friendships.get(id = kwargs['id'])
        friendship.status = "Declined"
        friendship.save()
        data = FriendshipSerializer(friendships)
        return JsonResponse(data.data, safe=False)

    @method_decorator(csrf_exempt)
    def post(self, request):
        user_account = request.user.accounts.get(account_id=request.session['account_id'])
        friend_username = request.POST.get('friend_username')
        friend_id = request.POST.get('friend_id')
        try:
            friend_account = Account.objects.get(account_id=friend_id, username = friend_username)
            friend_request = Friendship.objects.get_or_create(sent=user_account, received=friend_account)
            data = FriendshipSerializer(friend_request, many=True)
        except:
            return JsonResponse({"error": "Account not found."}, status = 404)
        
        
        