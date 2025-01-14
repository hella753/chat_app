from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone
from versatileimagefield.fields import VersatileImageField
from user.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model
    """
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    image = VersatileImageField(
        'Image',
        upload_to='user/images/',
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(
        verbose_name=_('Date joined'),
        default=timezone.now
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_('Staff')
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name=_('Superuser')
    )
    friends = models.ManyToManyField('self', blank=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()
