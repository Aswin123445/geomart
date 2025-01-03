# Generated by Django 5.1.3 on 2024-12-27 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0006_remove_payment_transaction_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_canceled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='refund_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.IntegerField(choices=[(1, 'Active'), (0, 'Canceled'), (2, 'delivered')], default=1),
        ),
    ]
