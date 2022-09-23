# Generated by Django 4.1.1 on 2022-09-23 18:24

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('middle_name', models.CharField(max_length=255, verbose_name='Отчество')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
                ('avatar', models.ImageField(upload_to='', verbose_name='Аватар')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('parents', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Родители')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('is_hidden', models.BooleanField(verbose_name='Скрыта')),
                ('is_markable', models.BooleanField(verbose_name='Оцениваемая')),
                ('order', models.IntegerField(verbose_name='Номер в списке курса')),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('hash', models.CharField(max_length=64, unique=True, verbose_name='Хеш файла')),
                ('size', models.IntegerField(verbose_name='Размер')),
                ('mime_type', models.CharField(max_length=255, verbose_name='MIME-тип')),
                ('data', models.FileField(upload_to='', verbose_name='Содержимое')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец')),
            ],
        ),
        migrations.CreateModel(
            name='Mark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=255, verbose_name='Значение')),
                ('comment', models.TextField(verbose_name='Коментарий')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student', to=settings.AUTH_USER_MODEL, verbose_name='Учащийся')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher', to=settings.AUTH_USER_MODEL, verbose_name='Преподаватель')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('sent_at', models.DateTimeField(verbose_name='Отправлено в')),
                ('attachments', models.ManyToManyField(to='edu_lnmo.file', verbose_name='Вложения')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Отправитель')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
            ],
        ),
        migrations.CreateModel(
            name='ActivityBasic',
            fields=[
                ('activity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='edu_lnmo.activity')),
            ],
            bases=('edu_lnmo.activity',),
        ),
        migrations.CreateModel(
            name='ActivityLink',
            fields=[
                ('activity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='edu_lnmo.activity')),
                ('link', models.URLField(verbose_name='Ссылка')),
                ('embed', models.BooleanField(default=True, verbose_name='Встроено')),
            ],
            bases=('edu_lnmo.activity',),
        ),
        migrations.CreateModel(
            name='MarkDiscipline',
            fields=[
                ('mark_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='edu_lnmo.mark')),
            ],
            bases=('edu_lnmo.mark',),
        ),
        migrations.CreateModel(
            name='MarkFinal',
            fields=[
                ('mark_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='edu_lnmo.mark')),
                ('final_type', models.CharField(choices=[('Q1', '1 четверть'), ('Q2', '2 четверть'), ('Q3', '3 четверть'), ('Q4', '4 четверть'), ('H1', '1 полугодие'), ('H2', '2 полугодие'), ('Y', 'Годовая'), ('F', 'Итоговая')], default='F', max_length=2)),
            ],
            bases=('edu_lnmo.mark',),
        ),
        migrations.CreateModel(
            name='MessageNews',
            fields=[
                ('message_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='edu_lnmo.message')),
            ],
            options={
                'abstract': False,
            },
            bases=('edu_lnmo.message',),
        ),
        migrations.CreateModel(
            name='MessagePrivate',
            fields=[
                ('message_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='edu_lnmo.message')),
                ('is_read', models.BooleanField(verbose_name='Прочитано')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Получатель')),
            ],
            options={
                'abstract': False,
            },
            bases=('edu_lnmo.message',),
        ),
        migrations.CreateModel(
            name='EducationSpecialization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edu_lnmo.department', verbose_name='Подразделение учебного заведения')),
            ],
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started', models.DateField(verbose_name='Дата поступления')),
                ('finished', models.DateField(null=True, verbose_name='Дата завершения')),
                ('starting_class', models.IntegerField(verbose_name='Класс поступления')),
                ('finishing_class', models.IntegerField(verbose_name='Класс завершения')),
                ('specialization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edu_lnmo.educationspecialization', verbose_name='Направление обучения')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Учащийся')),
            ],
        ),
        migrations.AddField(
            model_name='department',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edu_lnmo.organization'),
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('students', models.ManyToManyField(related_name='students', to=settings.AUTH_USER_MODEL, verbose_name='Учащиеся')),
                ('teachers', models.ManyToManyField(related_name='teachers', to=settings.AUTH_USER_MODEL, verbose_name='Преподаватели')),
            ],
        ),
        migrations.AddField(
            model_name='activity',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edu_lnmo.course', verbose_name='Курс'),
        ),
        migrations.CreateModel(
            name='MarkActivity',
            fields=[
                ('mark_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='edu_lnmo.mark')),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edu_lnmo.activity', verbose_name='Активность')),
            ],
            bases=('edu_lnmo.mark',),
        ),
        migrations.CreateModel(
            name='ActivityTask',
            fields=[
                ('activity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='edu_lnmo.activity')),
                ('body', models.TextField()),
                ('due_date', models.DateTimeField(null=True, verbose_name='Срок сдачи')),
                ('attachments', models.ManyToManyField(to='edu_lnmo.file', verbose_name='Вложения')),
            ],
            options={
                'abstract': False,
            },
            bases=('edu_lnmo.activity', models.Model),
        ),
        migrations.CreateModel(
            name='ActivityMedia',
            fields=[
                ('activity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='edu_lnmo.activity')),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edu_lnmo.file', verbose_name='Файл')),
            ],
            bases=('edu_lnmo.activity',),
        ),
        migrations.CreateModel(
            name='ActivityGroup',
            fields=[
                ('activity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='edu_lnmo.activity')),
                ('children', models.ManyToManyField(related_name='children', to='edu_lnmo.activity')),
            ],
            bases=('edu_lnmo.activity',),
        ),
        migrations.CreateModel(
            name='ActivityArticle',
            fields=[
                ('activity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='edu_lnmo.activity')),
                ('body', models.TextField()),
                ('attachments', models.ManyToManyField(to='edu_lnmo.file', verbose_name='Вложения')),
            ],
            options={
                'abstract': False,
            },
            bases=('edu_lnmo.activity', models.Model),
        ),
        migrations.CreateModel(
            name='MessageTaskSubmission',
            fields=[
                ('messageprivate_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='edu_lnmo.messageprivate')),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edu_lnmo.activitytask', verbose_name='Задание')),
            ],
            options={
                'abstract': False,
            },
            bases=('edu_lnmo.messageprivate',),
        ),
    ]
