# Generated by Django 3.0.2 on 2020-01-15 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0004_launch_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='launch',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]
