# Generated by Django 3.1.4 on 2023-01-01 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('POST_collector', '0022_auto_20221204_0957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='podio_item',
            name='PARENT',
            field=models.ManyToManyField(related_name='_podio_item_PARENT_+', to='POST_collector.Podio_Item'),
        ),
    ]