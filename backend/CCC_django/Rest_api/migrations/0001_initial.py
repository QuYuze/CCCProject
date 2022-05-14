# Generated by Django 4.0.3 on 2022-05-01 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='heat_map',
            fields=[
                ('id', models.CharField(max_length=250, primary_key=True, serialize=False)),
                ('pos_sentiment', models.FloatField()),
                ('neg_sentiment', models.FloatField()),
                ('neu_sentiment', models.FloatField()),
                ('compound_sentiment', models.FloatField()),
                ('tweet_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'heat_map',
            },
        ),
    ]
