# Generated by Django 4.1.7 on 2023-03-23 15:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('licznik_czasu', '0008_remove_client_username_project_employee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='project_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='licznik_czasu.project'),
        ),
    ]
