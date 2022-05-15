# Generated by Django 4.0.3 on 2022-05-01 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Rest_api', '0002_database_update_time_example_output'),
    ]

    operations = [
        migrations.CreateModel(
            name='example_agg',
            fields=[
                ('region_code', models.AutoField(max_length=250, primary_key=True, serialize=False)),
                ('no_offensive', models.IntegerField()),
                ('region_full', models.CharField(max_length=250)),
            ],
            options={
                'db_table': 'example_agg',
            },
        ),
    ]
