# Generated by Django 4.2.14 on 2024-08-12 14:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_reviewrequest_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='pageresult',
            name='flaged',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='reviewrequest',
            name='bottom_margin',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reviewrequest',
            name='left_margin',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reviewrequest',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='core.reviewrequest'),
        ),
        migrations.AddField(
            model_name='reviewrequest',
            name='right_margin',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reviewrequest',
            name='top_margin',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
