def add_variable_to_context(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        print(request.user.accounts.get(account_id = request.session['account_id']))

        return {
            'Accounts': request.user.accounts.all(),
            'curr_acc': request.user.accounts.get(account_id = request.session['account_id']),
            'Suggested_Sites': request.user.accounts.get(account_id = request.session['account_id']).suggested_sites.order_by('-site_ranking')
        }
    else:
        return {}