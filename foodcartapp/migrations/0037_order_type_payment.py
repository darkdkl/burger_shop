# Generated by Django 3.0.7 on 2020-08-26 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0036_auto_20200826_1453'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='type_payment',
            field=models.CharField(blank=True, choices=[('cashless', 'Безналичный'), ('cash', 'Наличный')], max_length=8),
        ),
    ]
