# Generated by Django 2.1.7 on 2019-03-30 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brat', '0009_tagingdatarate'),
    ]

    operations = [
        migrations.AddField(
            model_name='tagingdata',
            name='taging_is_taging',
            field=models.BooleanField(default=False),
        ),
    ]
