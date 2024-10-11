# Generated by Django 5.1.2 on 2024-10-11 22:33

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
            name='PullRequestDescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pr_number', models.IntegerField()),
                ('description', models.TextField(max_length=255)),
                ('task_id', models.CharField(blank=True, max_length=255, null=True)),
                ('repo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repositories.bookmarkedrepo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
