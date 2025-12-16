from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
    
        # Generate a dummy username from email
        username = email.split('@')[0]
        # Ensure uniqueness by appending random string if needed
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('client', 'Client'),
        ('caregiver', 'Caregiver'),
        ('admin', 'Admin'),
    )
    
    email = models.EmailField(_('email address'), unique=True)
    # Add a dummy username field that's not required
    username = models.CharField(
        _('username'), 
        max_length=150, 
        blank=True, 
        null=True,  # Allow null
        help_text=_('Optional. Not used for login.')
    )
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    user_type = models.CharField(_('user type'), max_length=20, choices=USER_TYPE_CHOICES, default='client')
    
    # Keep USERNAME_FIELD as email
    USERNAME_FIELD = 'email'
    # Make username optional in REQUIRED_FIELDS
    REQUIRED_FIELDS = []

    user_type = models.CharField(_('user type'), max_length=20, choices=USER_TYPE_CHOICES, default='client')
    
    # Profile completion tracking
    profile_completed = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('verified', 'Verified'),
            ('rejected', 'Rejected'),
        ),
        default='pending'
    )
    
    # Timestamps
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_login = models.DateTimeField(_('last login'), auto_now=True)
    
    # Permissions
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_superuser = models.BooleanField(_('superuser status'), default=False)
    
    # GDPR & compliance
    terms_accepted = models.BooleanField(default=False)
    privacy_policy_accepted = models.BooleanField(default=False)
    marketing_opt_in = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.email
    
    @property
    def is_client(self):
        return self.user_type == 'client'
    
    @property
    def is_caregiver(self):
        return self.user_type == 'caregiver'