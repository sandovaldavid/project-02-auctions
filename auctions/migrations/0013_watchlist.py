# Generated by Django 5.1.2 on 2024-11-28 01:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('auctions', '0012_alter_bid_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='watchlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='watchlist',
                                              to='auctions.listing')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='watchlist',
                                           to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
