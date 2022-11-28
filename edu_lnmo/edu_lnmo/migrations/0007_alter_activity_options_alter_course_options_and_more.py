# Generated by Django 4.1.1 on 2022-11-24 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edu_lnmo', '0006_multitoken'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'verbose_name': 'Активность', 'verbose_name_plural': 'Активности'},
        ),
        migrations.AlterModelOptions(
            name='course',
            options={'verbose_name': 'Курс', 'verbose_name_plural': 'Курсы'},
        ),
        migrations.AlterModelOptions(
            name='courseenrollment',
            options={'verbose_name': 'Запись на курс', 'verbose_name_plural': 'Записи на курсы'},
        ),
        migrations.AlterModelOptions(
            name='department',
            options={'verbose_name': 'Отдел', 'verbose_name_plural': 'Отделы'},
        ),
        migrations.AlterModelOptions(
            name='education',
            options={'verbose_name': 'Обучение', 'verbose_name_plural': 'Обучения'},
        ),
        migrations.AlterModelOptions(
            name='educationspecialization',
            options={'verbose_name': 'Направление обучения', 'verbose_name_plural': 'Направления обучения'},
        ),
        migrations.AlterModelOptions(
            name='file',
            options={'verbose_name': 'Файл', 'verbose_name_plural': 'Файлы'},
        ),
        migrations.AlterModelOptions(
            name='mark',
            options={'verbose_name': 'Оценка', 'verbose_name_plural': 'Оценки'},
        ),
        migrations.AlterModelOptions(
            name='message',
            options={'verbose_name': 'Сообщение', 'verbose_name_plural': 'Сообщения'},
        ),
        migrations.AlterModelOptions(
            name='messagethread',
            options={'verbose_name': 'Тема сообщений', 'verbose_name_plural': 'Темы сообщений'},
        ),
        migrations.AlterModelOptions(
            name='multitoken',
            options={'verbose_name': 'Токен', 'verbose_name_plural': 'Токены'},
        ),
        migrations.AlterModelOptions(
            name='olympiad',
            options={'verbose_name': 'Олимпиада', 'verbose_name_plural': 'Олимпиады'},
        ),
        migrations.AlterModelOptions(
            name='olympiadparticipation',
            options={'verbose_name': 'Участие в олимпиаде', 'verbose_name_plural': 'Участия в олимпиадах'},
        ),
        migrations.AlterModelOptions(
            name='organization',
            options={'verbose_name': 'Организация', 'verbose_name_plural': 'Организации'},
        ),
        migrations.AlterModelOptions(
            name='permission',
            options={'verbose_name': 'Право доступа', 'verbose_name_plural': 'Права доступа'},
        ),
        migrations.AlterModelOptions(
            name='threadgroup',
            options={'verbose_name': 'Группа тем сообщений', 'verbose_name_plural': 'Группы тем сообщений'},
        ),
        migrations.AlterModelOptions(
            name='unreadobject',
            options={'verbose_name': 'Непрочитанное', 'verbose_name_plural': 'Непрочитанные'},
        ),
        migrations.AlterField(
            model_name='course',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание'),
        ),
    ]