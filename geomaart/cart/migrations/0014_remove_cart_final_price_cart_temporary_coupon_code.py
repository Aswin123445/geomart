# Generated by Django 5.1.3 on 2025-01-06 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0013_alter_cartitem_total_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='final_price',
        ),
        migrations.AddField(
            model_name='cart',
            name='temporary_coupon_code',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
