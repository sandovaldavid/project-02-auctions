# Generated by Django 5.1.2 on 2024-11-28 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0013_watchlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='watchlist',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
