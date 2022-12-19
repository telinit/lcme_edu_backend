# Generated by Django 4.1.1 on 2022-12-07 10:07

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edu_lnmo', '0009_alter_activity_hours_alter_activity_marks_limit_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='weight',
            field=models.FloatField(default=1, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Вес оценок'),
        ),
    ]