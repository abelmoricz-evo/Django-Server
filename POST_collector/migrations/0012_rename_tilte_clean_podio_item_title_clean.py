# Generated by Django 4.0.6 on 2022-08-09 04:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('POST_collector', '0011_podio_item_tilte_clean'),
    ]

    operations = [
        migrations.RenameField(
            model_name='podio_item',
            old_name='Tilte_clean',
            new_name='Title_clean',
        ),
    ]