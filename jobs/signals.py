from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, ResumeApplication

# Unified User post_save signal
@receiver(post_save, sender=User)
def handle_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a profile with the appropriate role
        role = getattr(instance, '_role', 'seeker')
        Profile.objects.create(user=instance, role=role)
    else:
        # Save the profile if it exists
        if hasattr(instance, 'profile'):
            instance.profile.save()

# ResumeApplication auto-scoring
@receiver(post_save, sender=ResumeApplication)
def auto_score_resume(sender, instance, created, **kwargs):
    if created:
        instance.compute_score()
