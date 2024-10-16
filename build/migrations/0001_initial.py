# Generated by Django 5.1.2 on 2024-10-11 12:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('repositories', '0003_bookmarkedrepo_img_url'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BuildSystem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_update', models.DateTimeField(null=True)),
                ('error', models.TextField(blank=True, null=True)),
                ('task_id', models.CharField(blank=True, max_length=255, null=True)),
                ('repo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repositories.bookmarkedrepo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BuildSystemFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('purpose', models.TextField(blank=True)),
                ('icon', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('build_system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='build.buildsystem')),
            ],
        ),
        migrations.CreateModel(
            name='BuildSystemFileRecommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('action', models.CharField(max_length=255)),
                ('icon', models.CharField(max_length=255)),
                ('benefit', models.TextField(blank=True)),
                ('build_system_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='build.buildsystemfile')),
            ],
        ),
    ]
