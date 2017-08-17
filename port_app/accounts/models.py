# -*- coding: utf-8 -*-
from django.core import validators
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager, BaseUserManager
from django.conf import settings
import os
from auditlog.registry import auditlog


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_active=True,
                          is_superuser=is_superuser,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True,
                                 **extra_fields)
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser, PermissionsMixin):
    # telephone field validator
    telephone_validator = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                         message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    """
    An abstract base class implementing a fully featured User model with
    user-compliant permissions.

    Email and password are required. Other fields are optional.
    """
    first_name = models.CharField(_('first name'), max_length=255, )
    last_name = models.CharField(_('last name'), max_length=255, )
    email = models.EmailField(_('email address'), unique=True, max_length=255)
    telephone = models.CharField(_('telephone'), max_length=25, blank=True, null=True, validators=[telephone_validator])
    passport = models.CharField(_('Passport'), max_length=25, blank=True, null=True, )
    is_active = models.BooleanField(_('active'), default=False,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    # activation confirm
    activation_key = models.CharField(max_length=250, blank=True, null=True, unique=True)
    expiration_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-id']

    """
        Important non-field stuff
    """
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    def get_absolute_url(self):
        return reverse('accounts:user-detail', kwargs={'pk': self.pk})

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        if self.first_name or self.last_name:
            full_name = '{} {}'.format(self.first_name, self.last_name)
        else:
            full_name = self.email
        return full_name.strip()

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    # helpers for defining user level
    @property
    def is_user(self):
        groups = [group.name for group in self.groups.all()]
        return ('user' in groups)

    @property
    def is_agent(self):
        groups = [group.name for group in self.groups.all()]
        return ('agent' in groups or 'broker' in groups)

    @property
    def is_cashier(self):
        groups = [group.name for group in self.groups.all()]
        return ('cashier' in groups)

    @property
    def is_supervisor(self):
        groups = [group.name for group in self.groups.all()]
        return ('supervisor' in groups)

    @property
    def is_dispatcher(self):
        groups = [group.name for group in self.groups.all()]
        return ('dispatcher' in groups)

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    @property
    def get_status(self):
        if self.is_active:
            return "active"
        else:
            return "suspended"

    @property
    def user_group(self):
        if self.groups.all():
            return self.groups.all()[0]
        else:
            return ''

    def __str__(self):
        return "{} : {}".format(self.get_full_name(), self.email)

    def __init__(self, *args, **kwargs):
        super(MyUser, self).__init__(*args, **kwargs)
        self.is_active_cache = self.is_active

    class Meta:
        permissions = (
            ("user_view", "Can view User"),
            ("user_all_view", "Can view ALL User"),
            ("user_super_create", "Can view super create User"),
        )


auditlog.register(MyUser)


# Agentlikler
class Agent(models.Model):
    owner = models.OneToOneField(MyUser, verbose_name=_("Owner"), limit_choices_to={'groups__name': 'agent'})
    name = models.CharField(max_length=25, verbose_name=_("Agency Name"))
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Agent')
        verbose_name_plural = _('Agents')
        permissions = (
            ("agent_view", "Can view Agent"),
            ("agent_all_view", "Can view ALL Agent"),
            ("agent_object_owner", "Can own Agent"),
        )
        # def get_absolute_url(self):
        #     return reverse('accounts:agent-detail', kwargs={'pk': self.pk})


auditlog.register(Agent)
