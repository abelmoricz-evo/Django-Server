# Generated by Django 3.2.8 on 2022-10-02 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('POST_collector', '0020_alter_podio_item_file_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='podio_item',
            name='Estimated_hours',
            field=models.CharField(blank=True, max_length=12800),
        ),
        migrations.AlterField(
            model_name='podio_item',
            name='Podio_Best_Practices',
            field=models.CharField(blank=True, max_length=6400),
        ),
        migrations.AlterField(
            model_name='podio_item',
            name='Team',
            field=models.CharField(blank=True, max_length=6400),
        ),
    ]
