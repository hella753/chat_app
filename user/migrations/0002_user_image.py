# Generated by Django 5.1.4 on 2025-01-09 18:50

import versatileimagefield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image',
            field=versatileimagefield.fields.VersatileImageField(blank=True, upload_to='user/images/', verbose_name='Image'),
        ),
    ]
