from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Client, User, Employee


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    try:
        if created:
            if User.who_is == 'Client':
                Client.objects.create(user=instance).save()
            else:
                Employee.objects.create(user=instance).save()
    except Exception as err:
        print(f'Error creating user profile!\n{err}')
