# Generated by Django 5.1.2 on 2024-11-30 06:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('auctions', '0014_watchlist_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(blank=True),
        ),
    ]
