# Generated by Django 4.0.3 on 2022-05-14 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Rest_api', '0009_aggmap_new_fav_food'),
    ]

    operations = [
        migrations.AddField(
            model_name='mainsuburb',
            name='total_tweet',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]