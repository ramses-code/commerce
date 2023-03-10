# Generated by Django 4.1.3 on 2022-12-23 22:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_remove_bids_author_bids_bidder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bids',
            name='listing',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bid_listing', to='auctions.listings'),
        ),
    ]
