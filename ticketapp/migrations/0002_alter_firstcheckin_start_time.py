# Generated by Django 5.0.6 on 2024-11-30 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='firstcheckin',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
