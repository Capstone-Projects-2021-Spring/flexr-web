from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import json
import pytz
import traceback

from ..models import *
from ..forms import *
from ..serializers import HistorySerializer



class HistoryView(LoginRequiredMixin, View):
    """
    View class for the history page
    """

    def get(self, request, *args, **kwargs):
        """
        Display the history page
        """
        
        # get current user and current account
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

        # get all user's accounts and history
        accounts = curr_user.accounts.all()
        history = curr_account.history.all()

        # get history form object on the page
        form = FilterHistoryForm

        # request messages for debugging
        if ('message' in request.session):
            message = request.session['message']
            del request.session['message']
            messages.success(request, message)

        elif ('err_message' in request.session):
            message = request.session['err_message']
            del request.session['err_message']
            messages.error(request, message)

        request.session['redirect_url'] = '/browsing_history/'
        # display the page
        return render(request, "flexr_web/browsing_history.html",
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


    def delete(self, request, *args, **kwargs):
        """
        Delete requested history objects
        """

        # get current user and current account
        curr_user = request.user
        curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

        # get history objects to delete
        delete = request.POST.getlist('DELETE', [])
        print(delete)
        for x in delete:
            print(x)
            if (curr_account.history.filter(id=int(x)).count() == 0):
                delete.remove(x)
        if(len(delete) == 0):
            request.session['err_message'] = "History does not exist"
            return redirect(request.session['redirect_url'])
        # delete requested history objects
        curr_account.history.filter(pk__in=delete).delete()

        # request message for debugging
        request.session['message'] = "History Deleted"

        # return to history page
        return redirect(request.session['redirect_url'])
        
@method_decorator(csrf_exempt, name='dispatch')
class HistoryViewAPI(LoginRequiredMixin, DetailView):
    def get(self, request, *args, **kwargs):
        url = request.path.split('/')

        if not url[-1]:
            url = url[:-1]

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

        try:
            curr_user = request.user
            curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
            history = History.objects.filter(account = curr_account)
            data = HistorySerializer(history, many=True)
            return JsonResponse(data.data, safe=False)
        
        except Exception as e:
            return JsonResponse({ "error": str(e), "traceback": traceback.extract_tb(e.__traceback__).format() }, status=500)

    def filter_history(self, request, *args, **kwargs):
        """
        Returns filtered all site history from the current account
                Parameters:
                    request.GET has a JSON object that has the filter type and typed
                Returns:
                    JSONRequest with success message and the SiteHistory objects or error message
        """

        try:
            curr_user = request.user
            curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

            payload = request.GET.dict()
            history = History.objects.filter(
                account = curr_account,
                visit_datetime__gte=payload['datetime_from'],
                visit_datetime__lte=payload['datetime_to'])
            data = HistorySerializer(history, many=True)
            return JsonResponse(data.data, safe=False)

        except Exception as e:
            return JsonResponse({ "error": str(e), "traceback": traceback.extract_tb(e.__traceback__).format() }, status=500)

    # delete history objects based on list of ids
    def post(self, request, *args, **kwargs):
        try:
            # get current user and current account
            curr_user = request.user
            curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
        
            # get history objects to delete
            data = json.loads(request.body) #request.POST.getlist('DELETE', [])

            delete = []
            if 'DELETE' in data:
                delete = data['DELETE']

            # delete requested history objects
            curr_account.history.filter(pk__in=delete).delete()

            return JsonResponse({"success": "histories deleted"})

        except Exception as e:
            return JsonResponse({ "error": str(e), "traceback": traceback.extract_tb(e.__traceback__).format() }, status=500)

    def delete(self, request, *args, **kwargs):
        url = request.path.split('/')

        if not url[-1]:
            url = url[:-1]

        if url[-1] == 'filter':
            return self.delete_history_range(request, *args, **kwargs)

        elif url[-1].isdigit():
            return self.delete_history_single(request, *args, **kwargs)

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
        try:
            curr_user = request.user
            curr_account = curr_user.accounts.get(account_id = request.session['account_id'])
            payload = json.loads(request.body)
            history = History.objects.filter(
                account = curr_account,
                visit_datetime__gte=payload['datetime_from'],
                visit_datetime__lte=payload['datetime_to']).delete()

            return JsonResponse({"success": "histories deleted"})

        except Exception as e:
            return JsonResponse({ "error": str(e), "traceback": traceback.extract_tb(e.__traceback__).format() }, status=500)

    def delete_all_history(self, request, *args, **kwargs):
        """
        Deletes all history from a user
                Parameters:
                    request.DELETE
                Returns:
                    JSONRequest with success message or error message
        """
        try:
            curr_user = request.user
            curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

            history = History.objects.filter(account = curr_account).delete()

            return JsonResponse({"success": "all history deleted"})

        except Exception as e:
            return JsonResponse({ "error": str(e), "traceback": traceback.extract_tb(e.__traceback__).format() }, status=500)


    def delete_history_single(self, request, *args, **kwargs):
        try:
            curr_user = request.user
            curr_account = curr_user.accounts.get(account_id = request.session['account_id'])

            History.objects.filter(account = curr_account, id=kwargs['id']).delete()

            return JsonResponse({"success": "history object deleted"})

        except Exception as e:
            return JsonResponse({ "error": str(e), "traceback": traceback.extract_tb(e.__traceback__).format() }, status=500)