# Generated by Django 5.0.1 on 2025-03-09 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0003_remove_customuser_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='username',
            field=models.CharField(blank=True, max_length=300, null=True, unique=True),
        ),
    ]
