# Generated by Django 2.2.3 on 2019-09-10 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_auto_20190909_1409'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='activity_status',
        ),
        migrations.AddField(
            model_name='user',
            name='token',
            field=models.CharField(default='', max_length=256, verbose_name='融云token'),
        ),
    ]
