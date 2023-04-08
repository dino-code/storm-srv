from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from django.db import models

class UserProfile(models.Model):
    TIER_CHOICES = [
        ('STATIC', 'Static'),
        ('SPARK', 'Spark'),
        ('LIGHTNING', 'Lightning'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='FREE')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    job_title = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    social_media_links = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
