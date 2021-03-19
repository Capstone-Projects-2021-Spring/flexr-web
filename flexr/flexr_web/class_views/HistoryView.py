from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

import pytz

from ..models import *
from ..forms import *

# TODO: Gerald add request messages
# TODO: Gerald add delete history button

class HistoryView(LoginRequiredMixin, View):
    """
    View class for the history page
    """

    def get(self, *args, **kwargs):
        """
        Display the history page
        """
        
        # get current user and current account
        curr_user = self.request.user
        curr_account = curr_user.accounts.get(account_id = self.request.session['account_id'])

        # get all user's accounts and history
        accounts = curr_user.accounts.all()
        history = curr_account.history.all()

        # get history form object on the page
        form = FilterHistoryForm
        # display the page
        return render(self.request, "flexr_web/browsing_history.html",
         {"History": history, 
          "Accounts": accounts,
          "form": form})


    def filter(self, request, *args, **kwargs):
        """
        Filter the account's history by datetime range
        """

        # get current user and current account
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

        # get all user's accounts
        accounts = curr_user.accounts.all()

        # get form object on page
        form = FilterHistoryForm

        # grab date and time information from POST form
        start_date = request.POST['start_date']
        start_time = request.POST['start_time']
        end_date = request.POST['end_date']
        end_time = request.POST['end_time']

        # concat to datetime format
        start_datetime = start_date + ' ' + start_time
        end_datetime = end_date + ' ' + end_time

        # construct datetime object with timezone
        # TODO: Gerald check that timezone's work correctly
        start = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M').replace(tzinfo = pytz.UTC)
        end = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M').replace(tzinfo = pytz.UTC)
        

        # filter history based on given start and end datetimes
        history = curr_account.history.filter(
            visit_datetime__gte=start,
            visit_datetime__lte=end
        )

        return redirect('/browsing_history/')


    # TODO: Gerald
    def delete(self, *args, **kwargs):
        """
        Delete a history object
        """
        pass