from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from user.models import User
from user.utils.activation_token_generator import account_activation_token
from celery import shared_task


@shared_task
def send_verification_email(user_id, current_site_domain, email_address):
    """
    This function is used to send a verification email to a user.
    The email contains a link to verify the account of the user.
    """
    user = User.objects.get(pk=user_id)
    mail_subject = 'Activate your account'
    message = render_to_string('authorization/verification-email.html', {
        'user': user,
        'domain': current_site_domain,
        'uid': user.pk,
        'token': account_activation_token.make_token(user),
    })
    to_email = email_address
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.content_subtype = 'html'
    email.send()