# Generated by Django 5.1.2 on 2024-10-17 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pr_manager', '0004_reviewfinding_recommendation_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pullrequestreview',
            name='pr_number',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
