# Generated by Django 4.2.14 on 2024-07-31 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviewrequest',
            name='status',
            field=models.CharField(default='pending', max_length=100),
        ),
    ]
