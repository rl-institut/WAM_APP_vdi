# Generated by Django 2.1.3 on 2019-03-22 16:23

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stemp_abw', '0012_scenario_repowering_scenario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repoweringscenario',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=None),
        ),
    ]