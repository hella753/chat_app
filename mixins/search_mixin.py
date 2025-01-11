from django.shortcuts import redirect


class SearchMixIn:
    """
    Mixin for search to redirect to profile detail
    view if username is provided in the search field.
    """
    def get(self, request, *args, **kwargs):
        username = request.GET.get('username')
        if username and username != request.user.username:
            return redirect('accounts:profile_detail', username=username)
        return super().get(request, *args, **kwargs)