# Generated by Django 4.0.6 on 2022-08-06 18:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('POST_collector', '0005_podio_application_last_updated_on_heroku'),
    ]

    operations = [
        migrations.CreateModel(
            name='Podio_Hook',
            fields=[
                ('hook_id', models.CharField(blank=True, max_length=400, primary_key=True, serialize=False)),
                ('url', models.CharField(blank=True, max_length=400)),
                ('hook_type', models.CharField(blank=True, max_length=400)),
                ('status', models.CharField(blank=True, max_length=400)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='POST_collector.podio_application')),
            ],
        ),
    ]
