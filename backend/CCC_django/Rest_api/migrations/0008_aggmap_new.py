# Generated by Django 4.0.3 on 2022-05-13 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Rest_api', '0007_mainsuburb'),
    ]

    operations = [
        migrations.CreateModel(
            name='aggmap_new',
            fields=[
                ('display_order', models.IntegerField(primary_key=True, serialize=False)),
                ('crime_rate', models.FloatField()),
                ('sent_score', models.FloatField()),
                ('no_offensive', models.IntegerField()),
                ('region_full', models.CharField(max_length=250)),
            ],
            options={
                'db_table': 'aggmap_new',
            },
        ),
    ]
