# Generated by Django 5.1.2 on 2024-11-27 23:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_listing_current_bid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10),
        ),
    ]
