# Generated by Django 2.2.9 on 2020-03-07 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0008_auto_20200229_1731'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='delivery',
            field=models.CharField(default='🚗 Привезти', max_length=15, verbose_name='тип доставки'),
        ),
    ]
