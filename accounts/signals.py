from django.dispatch import receiver
from django.db.models.signals import post_save
# from django.contrib.auth.models import MyUser
from accounts.models import MyUser, CareSeeker, CareTaker, Profile
from django.conf import settings
from rest_framework.authtoken.models import Token



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    # instance.is_younger
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_care_user(sender, instance, created, **kwargs):
    if created:
        if instance.care_taker:
            CareTaker.objects.create(user=instance)
        else:
            CareSeeker.objects.create(user=instance)