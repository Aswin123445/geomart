# Generated by Django 5.1.3 on 2024-12-05 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userdata_is_email_verified_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdata',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='OTP',
        ),
    ]