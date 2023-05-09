from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_out
from .models import Client, User, Employee, TaskTimer
from django.utils import timezone
from .views import StopThread


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    try:
        if created:
            if instance.who_is == 'CL':
                Client.objects.create(user=instance).save()
            elif instance.who_is == 'EM':
                Employee.objects.create(user=instance).save()
            else:
                print('Error!')
    except Exception as err:
        print(f'Błąd podczas tworzenia profilu.\n{err}')
