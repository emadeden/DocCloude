# Generated by Django 4.2 on 2023-06-23 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('container_management', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='container',
            name='ip_address',
            field=models.CharField(max_length=39),
        ),
    ]
