# Generated by Django 5.1.2 on 2024-10-17 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pr_manager', '0002_pullrequestreview_reviewfinding'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pullrequestreview',
            name='summary',
            field=models.TextField(null=True),
        ),
    ]
