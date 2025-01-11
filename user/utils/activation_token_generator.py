from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    This class is used to generate a token for account activation.
    """
    pass

account_activation_token = AccountActivationTokenGenerator()