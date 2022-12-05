# Generated by Django 4.0.5 on 2022-08-06 07:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Podio_Item',
            fields=[
                ('item_id', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('link', models.CharField(blank=True, max_length=400)),
                ('last_event_on', models.DateTimeField(blank=True, null=True)),
                ('created_on', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.CharField(blank=True, max_length=400)),
                ('last_updated_on_heroku', models.DateTimeField(auto_now=True)),
                ('app_name', models.CharField(blank=True, max_length=400)),
                ('app_id', models.CharField(blank=True, max_length=400)),
                ('space_id', models.CharField(blank=True, max_length=400)),
                ('SPACE', models.CharField(blank=True, max_length=1600)),
                ('Title', models.CharField(blank=True, max_length=1600)),
                ('Due_Date', models.DateTimeField(blank=True, null=True)),
                ('Estimated_hours', models.CharField(blank=True, max_length=1600)),
                ('Goal', models.CharField(blank=True, max_length=1600)),
                ('Status', models.CharField(choices=[('-', 'NO STATUS'), ('planned', 'Planned'), ('new', 'New'), ('approved', 'Approved'), ('in progress', 'In Progress'), ('revision', 'Revision'), ('done', 'Done'), ('on hold', 'On Hold'), ('cancelled', 'Cancelled')], default='-', max_length=11)),
                ('Approach', models.CharField(blank=True, max_length=1600)),
                ('Constraints_and_assumptions', models.CharField(blank=True, max_length=1600)),
                ('Target_result_description', models.CharField(blank=True, max_length=1600)),
                ('On_hold_cancellation_reason', models.CharField(blank=True, max_length=1600)),
                ('Problem_Statement', models.CharField(blank=True, max_length=1600)),
                ('Responsible', models.CharField(blank=True, max_length=1600)),
                ('Accountable', models.CharField(blank=True, max_length=1600)),
                ('Start_Date', models.DateTimeField(blank=True, null=True)),
                ('Outcome', models.CharField(blank=True, max_length=1600)),
                ('Notes', models.CharField(blank=True, max_length=1600)),
                ('Team', models.CharField(blank=True, max_length=1600)),
                ('PARENT', models.CharField(blank=True, max_length=1600)),
                ('File_location', models.CharField(blank=True, max_length=1600)),
                ('organization_sales', models.CharField(blank=True, max_length=1600)),
                ('organization_id_sales', models.CharField(blank=True, max_length=1600)),
                ('organization_ranking_sales', models.CharField(blank=True, max_length=1600)),
                ('sales_call_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ('SPACE',),
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('slug', models.SlugField(max_length=250, unique_for_date='publish')),
                ('body', models.TextField()),
                ('publish', models.DateTimeField(default=django.utils.timezone.now)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published')], default='draft', max_length=10)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-publish',),
            },
        ),
    ]