# Generated by Django 2.2.9 on 2020-02-22 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='arrr',
            name='unic',
            field=models.CharField(blank=True, max_length=250, null=True, unique=True),
        ),
    ]
