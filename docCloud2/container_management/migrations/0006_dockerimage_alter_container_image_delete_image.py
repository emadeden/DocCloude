# Generated by Django 4.2 on 2023-06-28 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('container_management', '0005_container_cpu_share_container_memory_limit'),
    ]

    operations = [
        migrations.CreateModel(
            name='DockerImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('tag', models.CharField(max_length=255)),
                ('image_id', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('size', models.PositiveIntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='container',
            name='image',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='container_management.dockerimage'),
        ),
        migrations.DeleteModel(
            name='Image',
        ),
    ]
