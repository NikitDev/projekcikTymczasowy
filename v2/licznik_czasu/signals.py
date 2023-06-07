from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from .models import Client, User, Employee


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
        pass


@receiver(pre_save, sender=User)
def update_user(sender, instance, **kwargs):
    try:
        if instance.pk is not None:

            try:
                client = instance.client
                if instance.who_is == 'EM':
                    client.delete()
                    Employee.objects.create(user=instance).save()

            except Exception as err:
                pass

            try:
                employee = instance.employee
                if instance.who_is == 'CL':
                    employee.delete()
                    Client.objects.create(user=instance).save()

            except Exception:
                pass

    except Exception:
        pass
