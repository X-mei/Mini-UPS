# Generated by Django 3.1.5 on 2021-04-23 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0011_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='package',
            name='id',
        ),
        migrations.AlterField(
            model_name='package',
            name='package_id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
