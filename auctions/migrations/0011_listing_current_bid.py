# Generated by Django 5.1.2 on 2024-11-27 22:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('auctions', '0010_alter_listing_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='current_bid',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
