# Generated by Django 2.1.3 on 2019-03-21 21:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stemp_abw', '0008_scenario_data'),
    ]

    operations = [
        migrations.DeleteModel(
            name='RegMunStats',
        ),
        migrations.CreateModel(
            name='RegMunDemElEnergy',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('stemp_abw.regmun',),
        ),
        migrations.CreateModel(
            name='RegMunDemThEnergy',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('stemp_abw.regmun',),
        ),
        migrations.CreateModel(
            name='RegMunGenCapRe',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('stemp_abw.regmun',),
        ),
        migrations.CreateModel(
            name='RegMunGenCountWindDensity',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('stemp_abw.regmun',),
        ),
        migrations.CreateModel(
            name='RegMunGenEnergyRe',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('stemp_abw.regmun',),
        ),
        migrations.CreateModel(
            name='RegMunPop',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('stemp_abw.regmun',),
        ),
        migrations.CreateModel(
            name='RegMunPopDensity',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('stemp_abw.regmun',),
        ),
        migrations.CreateModel(
            name='RegMunDemElEnergyPerCapita',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('stemp_abw.regmundemelenergy',),
        ),
        migrations.CreateModel(
            name='RegMunDemThEnergyPerCapita',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('stemp_abw.regmundemthenergy',),
        ),
        migrations.CreateModel(
            name='RegMunEnergyReElDemShare',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('stemp_abw.regmungenenergyre', 'stemp_abw.regmundemelenergy'),
        ),
        migrations.CreateModel(
            name='RegMunGenCapReDensity',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('stemp_abw.regmungencapre',),
        ),
        migrations.CreateModel(
            name='RegMunGenEnergyReDensity',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('stemp_abw.regmungenenergyre',),
        ),
        migrations.CreateModel(
            name='RegMunGenEnergyRePerCapita',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('stemp_abw.regmungenenergyre',),
        ),
    ]