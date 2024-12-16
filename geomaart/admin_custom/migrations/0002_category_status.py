# Generated by Django 5.1.3 on 2024-12-14 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_custom', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='status',
            field=models.IntegerField(choices=[(1, 'Active'), (2, 'Coming Soon'), (3, 'Inactive')], default=1),
        ),
    ]
