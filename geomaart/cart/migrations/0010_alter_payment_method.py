# Generated by Django 5.1.3 on 2025-01-03 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0009_wallet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='method',
            field=models.IntegerField(choices=[(1, 'Cash on Delivery'), (2, 'Credit/Debit Card'), (3, 'wallet')], default=1),
        ),
    ]
