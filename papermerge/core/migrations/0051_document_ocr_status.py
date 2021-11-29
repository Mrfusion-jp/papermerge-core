# Generated by Django 3.2.9 on 2021-11-29 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0050_alter_documentversion_short_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='ocr_status',
            field=models.CharField(choices=[('unknown', 'Unknown'), ('received', 'Received'), ('started', 'Started'), ('succeeded', 'Succeeded'), ('failed', 'Failed')], default='unknown', max_length=32),
        ),
    ]
