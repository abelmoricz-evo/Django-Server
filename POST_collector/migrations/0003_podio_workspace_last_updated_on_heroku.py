# Generated by Django 4.0.6 on 2022-08-06 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('POST_collector', '0002_podio_application_podio_workspace_delete_post_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='podio_workspace',
            name='last_updated_on_heroku',
            field=models.DateTimeField(auto_now=True),
        ),
    ]