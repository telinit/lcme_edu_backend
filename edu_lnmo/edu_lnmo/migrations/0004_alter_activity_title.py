# Generated by Django 4.1.1 on 2022-11-15 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edu_lnmo', '0003_messagethread_olympiad_olympiadparticipation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='title',
            field=models.TextField(verbose_name='Название'),
        ),
    ]