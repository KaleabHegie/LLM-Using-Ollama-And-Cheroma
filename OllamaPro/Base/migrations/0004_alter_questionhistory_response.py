# Generated by Django 4.2 on 2024-12-18 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Base', '0003_alter_loadedfile_number_questionhistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionhistory',
            name='response',
            field=models.TextField(blank=True, null=True),
        ),
    ]
