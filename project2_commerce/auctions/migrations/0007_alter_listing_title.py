# Generated by Django 5.1.2 on 2024-11-27 03:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('auctions', '0006_alter_listing_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='title',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
