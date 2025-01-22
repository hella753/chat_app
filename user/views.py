from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView, UpdateView, ListView, FormView

from chat.tasks import send_notification
from mixins.search_mixin import SearchMixIn
from user.forms import RegistrationForm, UpdatePasswordForm, ProfileUpdateForm
from user.models import User
from user.tasks import send_verification_email
from user.utils.activation_token_generator import account_activation_token


@method_decorator(login_required, name='dispatch')
class MyProfileView(SearchMixIn, TemplateView):
    """
    This view is used to display the profile of the logged-in user.
    """
    template_name = 'profile/profile.html'


class RegisterView(CreateView):
    """
    This view is used to register a new user.
    The user is created with the is_active flag set to False.
    An email is sent to the user with a link to activate the
    account.
    The user is redirected to the verified page.
    """
    template_name = 'authorization/register.html'
    success_url = reverse_lazy('accounts:verify')
    form_class = RegistrationForm

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        user.save()
        current_site = get_current_site(self.request)
        current_site_domain = current_site.domain
        email_address = form.cleaned_data.get('email')
        send_verification_email.delay(user.id, current_site_domain, email_address)
        return redirect(self.success_url)


@method_decorator(login_required, name='dispatch')
class ProfileDetailView(SearchMixIn, DetailView):
    """
    This view is used to display the profile of a user.
    The user is identified by the username.
    """
    model = User
    template_name = 'profile/profile-detail.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'


@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(SearchMixIn, UpdateView):
    """
    This view is used to update the profile of the logged-in user.
    """
    model = User
    template_name = 'profile/profile-update.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    success_url = reverse_lazy('accounts:profile')
    form_class = ProfileUpdateForm


@method_decorator(login_required, name='dispatch')
class ProfileUpdatePasswordView(SearchMixIn, UpdateView):
    """
    This view is used to update the password of the logged-in user.
    """
    model = User
    template_name = 'profile/profile-update-password.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    success_url = reverse_lazy('accounts:profile')
    form_class = UpdatePasswordForm


class VerificationView(View):
    """
    This view is used to verify the account of a user.
    The user is identified by the uid and token.
    If the token is valid, the is_active flag is set to True.
    The user is redirected to the activation success page.
    If the token is invalid, the user is deleted and the user is redirected
    to the activation failed page.
    """
    def get(self, request, uid, token):
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return HttpResponse('Activation link is invalid!')

        if account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return TemplateResponse(
                request,
                'authorization/activation-success.html'
            )
        else:
            user.delete()
            return TemplateResponse(
                request,
                'authorization/activation-failed.html'
            )


@method_decorator(login_required, name="dispatch")
class FriendListingView(SearchMixIn, ListView):
    """
    List all friends that the user has.
    """
    template_name = "profile/friends.html"
    model = User
    context_object_name = "friends"
    paginate_by = 6

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and isinstance(user, User):
            return user.friends.all()
        return User.objects.none()


@method_decorator(login_required, name="dispatch")
class FriendRequestListingView(SearchMixIn, ListView):
    """
    List all friend requests that the user has.
    """
    template_name = "profile/friend-requests.html"
    model = User
    context_object_name = "friend_requests"
    paginate_by = 6

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and isinstance(user, User):
            return user.friend_requests.all()
        return User.objects.none()


@method_decorator(login_required, name="dispatch")
class AddFriendRequestView(View):
    """
    Add a friend request to the user.
    """
    template_name = "profile/add-friend.html"
    success_url = reverse_lazy("accounts:profile")

    def post(self, request, username):
        try:
            friend = User.objects.get(username=username)
            friend.friend_requests.add(request.user)
            request.user.friend_requests.remove(friend)
            send_notification.delay(friend.id, f"New friend request!")


        except User.DoesNotExist:
            return redirect(self.success_url)
        return redirect(self.success_url)


@method_decorator(login_required, name="dispatch")
class AcceptFriendRequestView(View):
    """
    Accept a friend request from the user.
    """
    template_name = "profile/friend_requests.html"
    success_url = reverse_lazy("accounts:friend_requests")

    def post(self, request, username):
        user = request.user
        try:
            friend = User.objects.get(username=username)
            user.friends.add(friend)
            user.friend_requests.remove(friend)
            send_notification.delay(friend.id, f"Accepted your friend request!")
        except User.DoesNotExist:
            return redirect(self.success_url)
        return redirect(self.success_url)


@method_decorator(login_required, name="dispatch")
class DeclineFriendRequestView(View):
    """
    Decline a friend request from the user.
    """
    template_name = "profile/friend_requests.html"
    success_url = reverse_lazy("accounts:friend_requests")

    def post(self, request, username):
        user = request.user
        try:
            friend = User.objects.get(username=username)
            user.friend_requests.remove(friend)
        except User.DoesNotExist:
            return redirect(self.success_url)
        return redirect(self.success_url)


@method_decorator(login_required, name="dispatch")
class RemoveFriendView(View):
    """
    Remove a friend from the user.
    """
    template_name = "profile/friends.html"
    success_url = reverse_lazy("accounts:friends")

    def post(self, request, username):
        user = request.user
        try:
            friend = User.objects.get(username=username)
            user.friends.remove(friend)
        except User.DoesNotExist:
            return redirect(self.success_url)
        return redirect(self.success_url)


class PageNotFound(TemplateView):
    """
    This view is used to display the 404 page.
    """
    template_name = '404.html'


class InternalServerError(TemplateView):
    """
    This view is used to display the 500 page.
    """
    template_name = '500.html'