# Generated by Django 4.2 on 2024-12-25 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Base', '0006_chatinstance_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatinstance',
            name='title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
