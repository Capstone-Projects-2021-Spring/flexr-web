from .forms import *
def add_variable_to_context(request):
    if request.user.is_authenticated and request.user.accounts.all().count() > 0:
        return {
            'Accounts': request.user.accounts.all(),
            'curr_acc': request.user.accounts.get(account_id = request.session['account_id']),
            'Suggested_Sites': request.user.accounts.get(account_id = request.session['account_id']).suggested_sites.order_by('-site_ranking'),
            'acc_form': AccountForm()
            }
    else:
        return {}