# Generated by Django 5.1.2 on 2024-10-11 16:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('build', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='buildsystemfilerecommendation',
            name='task_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='buildsystemfile',
            name='build_system',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='build.buildsystem'),
        ),
        migrations.AlterField(
            model_name='buildsystemfilerecommendation',
            name='build_system_file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recommendations', to='build.buildsystemfile'),
        ),
    ]
