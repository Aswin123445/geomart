# Generated by Django 5.1.3 on 2024-12-24 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_remove_profile_social_links_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='address_type',
            field=models.IntegerField(choices=[(1, 'Home'), (2, 'Work'), (3, 'temporary')], default=1),
        ),
    ]