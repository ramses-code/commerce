# Generated by Django 4.1.3 on 2022-12-24 03:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_alter_bids_listing'),
    ]

    operations = [
        migrations.AddField(
            model_name='listings',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
