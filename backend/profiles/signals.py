from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import ClientProfile, CaregiverProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically creates the corresponding profile based on user type.
    """
    if instance.user_type == 'client':
        ClientProfile.objects.get_or_create(
            user=instance,
            defaults={
                'first_name': instance.first_name or instance.username,
                'last_name': instance.last_name or ""
            }
        )
    elif instance.user_type == 'caregiver':
        CaregiverProfile.objects.get_or_create(
            user=instance,
            defaults={
                'first_name': instance.first_name or instance.username,
                'last_name': instance.last_name or ""
            }
        )