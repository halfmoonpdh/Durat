# Generated by Django 2.1.7 on 2019-04-16 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brat', '0017_auto_20190412_1940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tagingdatarate',
            name='taging_log',
            field=models.TextField(blank=True, default=''),
        ),
    ]