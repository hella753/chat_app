from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView, UpdateView
from mixins.search_mixin import SearchMixIn
from user.forms import RegistrationForm, UpdatePasswordForm, ProfileUpdateForm
from user.models import User
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
        mail_subject = 'Activate your account'
        message = render_to_string('authorization/verification-email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': user.pk,
            'token': account_activation_token.make_token(user),
        })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.content_subtype = 'html'
        email.send()
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