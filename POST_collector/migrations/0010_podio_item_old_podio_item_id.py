# Generated by Django 4.0.6 on 2022-08-07 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('POST_collector', '0009_podio_item_podio_best_practices'),
    ]

    operations = [
        migrations.AddField(
            model_name='podio_item',
            name='old_podio_item_id',
            field=models.CharField(blank=True, max_length=1600),
        ),
    ]
