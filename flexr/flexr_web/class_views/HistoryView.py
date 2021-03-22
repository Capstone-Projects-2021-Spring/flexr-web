from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView

import json
import pytz

from ..models import *
from ..forms import *
from ..serializers import HistorySerializer


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

        # request messages for debugging
        if ('message' in self.request.session):
            message = self.request.session['message']
            del self.request.session['message']
            messages.success(self.request, message)

        elif ('err_message' in self.request.session):
            message = self.request.session['err_message']
            del self.request.session['err_message']
            messages.error(self.request, message)


        # display the page
        return render(self.request, "flexr_web/browsing_history.html",
         {"History": history, 
          "Accounts": accounts,
          "form": form})


    def post(self, request, *args, **kwargs):
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
        site = request.POST['site']
        start_date = request.POST['start_date']
        start_time = request.POST['start_time']
        end_date = request.POST['end_date']
        end_time = request.POST['end_time']

        # set default time if None
        if not start_time:
            start_time = '00:00'

        # set default time if None
        if not end_time:
            end_time = '00:00'

        # concat to datetime format
        start_datetime = start_date + ' ' + start_time
        end_datetime = end_date + ' ' + end_time

        # TODO: Gerald check that timezone's work correctly
        
        # grab all history objects
        history = curr_account.history.all()

        # filter based on site if given
        if site:
            history = history.filter(site__url__icontains=site)

        # filter based on start if given
        if start_date:
            start = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M').replace(tzinfo = pytz.UTC)
            history = history.filter(
            visit_datetime__gte=start)

        # filter based on end if given
        if end_date:
            end = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M').replace(tzinfo = pytz.UTC)
            history = history.filter(
            visit_datetime__lte=end
        )


        # request message for debugging
        request.session['message'] = "History Filtered"

        # Gerald: using redirect doesn't work here?
        return render(request, "flexr_web/browsing_history.html",
         {"History": history, 
          "Accounts": accounts,
          "form": form})


    # TODO: Gerald
    def delete(self, request, *args, **kwargs):
        """
        Delete requested history objects
        """

        # get current user and current account
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
    
        # get history objects to delete
        delete = request.POST.getlist('DELETE', [])

        # delete requested history objects
        curr_account.history.filter(pk__in=delete).delete()

        # request message for debugging
        request.session['message'] = "History Deleted"

        # return to history page
        return redirect('/browsing_history/')

class HistoryViewAPI(LoginRequiredMixin, DetailView):
    def get(self, request, *args, **kwargs):
        url = request.path.split('/')

        if url[-1] == 'filter':
            return self.filter_history(request, *args, **kwargs)
        else:
            return self.get_history(request, *args, **kwargs)



    def get_history(self, request, *args, **kwargs):
        """
        Gets all site history from the current account
                Parameters:
                    request.GET has an id for a site history
                Returns:
                    JSONRequest with success message and the SiteHistory instance or error message
        """

        history = History.objects.filter(account = kwargs["id"])
        data = HistorySerializer(history, many=True)
        return JsonResponse(data.data, safe=False)

    def filter_history(self, request, *args, **kwargs):
        """
        Returns filtered all site history from the current account
                Parameters:
                    request.GET has a JSON object that has the filter type and typed
                Returns:
                    JSONRequest with success message and the SiteHistory objects or error message
        """

        payload = request.GET.dict()
        history = History.objects.filter(
            account = kwargs["id"],
            visit_datetime__gte=payload['datetime_from'],
            visit_datetime__lte=payload['datetime_to'])
        data = HistorySerializer(history, many=True)
        return JsonResponse(data.data, safe=False)

    # delete history objects based on list of ids
    def post(self, request, *args, **kwargs):
        # get current user and current account
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
    
        # get history objects to delete
        delete = request.POST.getlist('DELETE', [])

        # delete requested history objects
        curr_account.history.filter(pk__in=delete).delete()

        return HttpResponse(f'History objects removed')

    def delete(self, request, *args, **kwargs):
        url = request.path.split('/')

        if url[-1] == 'filter':
            return self.delete_history_range(request, *args, **kwargs)
        else:
            return self.delete_all_history(request, *args, **kwargs)

    def delete_history_range(self, request, *args, **kwargs):
        """
        Deletes all history from a user within a given range
                Parameters:
                    request.DELETE has a JSON object that has a date range
                Returns:
                    JSONRequest with success message and the SiteHistory objects or error message
        """
        payload = json.loads(request.body)
        history = History.objects.filter(
            account = kwargs["id"],
            visit_datetime__gte=payload['datetime_from'],
            visit_datetime__lte=payload['datetime_to']).delete()

        return HttpResponse(f'{history} History objects removed')

    def delete_all_history(self, request, *args, **kwargs):
        """
        Deletes all history from a user
                Parameters:
                    request.DELETE
                Returns:
                    JSONRequest with success message or error message
        """

        history = History.objects.filter(account = kwargs["id"]).delete()

        return HttpResponse(f'{history} History objects removed')