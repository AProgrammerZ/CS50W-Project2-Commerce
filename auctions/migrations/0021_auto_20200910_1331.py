# Generated by Django 3.0.8 on 2020-09-10 17:31

import auctions.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0020_auto_20200910_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='category',
            field=models.CharField(default=auctions.models.testing_function, max_length=64),
        ),
    ]
