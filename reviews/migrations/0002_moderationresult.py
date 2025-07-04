# Generated by Django 5.2.3 on 2025-06-29 16:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModerationResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flagged', models.BooleanField()),
                ('categories', models.JSONField()),
                ('category_scores', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('review', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='moderation', to='reviews.review')),
            ],
        ),
    ]
