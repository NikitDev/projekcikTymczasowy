# Generated by Django 4.1.7 on 2023-04-05 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licznik_czasu', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='who_is',
            field=models.CharField(choices=[('CL', 'Client'), ('Em', 'Employee')], default='Client', max_length=8),
        ),
    ]
