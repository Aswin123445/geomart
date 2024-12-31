# Generated by Django 5.1.3 on 2024-12-28 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0007_order_is_canceled_order_refund_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='refund_status',
            field=models.IntegerField(choices=[(1, 'Pending'), (2, 'Completed'), (3, 'Failed')], default=1),
        ),
    ]