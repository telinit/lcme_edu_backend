# Generated by Django 4.1.1 on 2022-11-10 12:55

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import edu_lnmo.user.models
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
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('middle_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Отчество')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Аватар')),
                ('pw_enc', models.TextField(blank=True, null=True, verbose_name='Шифрованный пароль')),
                ('password', models.CharField(max_length=128, validators=[edu_lnmo.user.models.validate_password], verbose_name='password')),
                ('children', models.ManyToManyField(blank=True, related_name='parents', to=settings.AUTH_USER_MODEL, verbose_name='Дети')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
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
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('content_type', models.CharField(choices=[('GEN', 'Общая'), ('TXT', 'Текст'), ('TSK', 'Задание'), ('LNK', 'Ссылка'), ('MED', 'Медиа-контент'), ('FIN', 'Итоговый контроль')], default='GEN', max_length=3)),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('keywords', models.CharField(blank=True, max_length=255, verbose_name='Кодовое название')),
                ('lesson_type', models.CharField(blank=True, max_length=255, verbose_name='Тип занятия')),
                ('is_hidden', models.BooleanField(default=False, verbose_name='Скрыта')),
                ('marks_limit', models.IntegerField(default=1, verbose_name='Лимит оценок')),
                ('hours', models.IntegerField(default=1, verbose_name='Количество часов')),
                ('fgos_complient', models.BooleanField(default=False, verbose_name='Соответствие ФГОС')),
                ('order', models.IntegerField(verbose_name='Номер в списке курса')),
                ('date', models.DateField(verbose_name='Дата проведения')),
                ('group', models.CharField(blank=True, max_length=255, null=True, verbose_name='Группа')),
                ('scientific_topic', models.CharField(blank=True, max_length=255, null=True, verbose_name='')),
                ('body', models.TextField(blank=True)),
                ('due_date', models.DateTimeField(blank=True, null=True, verbose_name='Срок сдачи')),
                ('link', models.URLField(blank=True, null=True, verbose_name='Ссылка')),
                ('embed', models.BooleanField(default=True, verbose_name='Встроена')),
                ('final_type', models.CharField(blank=True, choices=[('Q1', '1 четверть'), ('Q2', '2 четверть'), ('Q3', '3 четверть'), ('Q4', '4 четверть'), ('H1', '1 полугодие'), ('H2', '2 полугодие'), ('Y', 'Годовая'), ('E', 'Экзамен'), ('F', 'Итоговая')], default='F', max_length=2, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(choices=[('GEN', 'Курс'), ('EDU', 'Учебная программа'), ('SEM', 'Семинар'), ('CLB', 'Кружок'), ('ELE', 'Предмет по выбору')], default='GEN', max_length=3)),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('for_class', models.CharField(blank=True, max_length=10, verbose_name='Класс')),
                ('for_group', models.CharField(blank=True, max_length=255, null=True, verbose_name='Группа')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('hash', models.CharField(max_length=64, unique=True, verbose_name='Хеш файла')),
                ('size', models.IntegerField(verbose_name='Размер')),
                ('mime_type', models.CharField(max_length=255, verbose_name='MIME-тип')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('body', models.TextField(blank=True)),
                ('sent_at', models.DateTimeField(verbose_name='Отправлено в')),
                ('attachments', models.ManyToManyField(blank=True, related_name='messages', to='edu_lnmo.file', verbose_name='Вложения')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages_sent', to=settings.AUTH_USER_MODEL, verbose_name='Отправитель')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('name_short', models.CharField(blank=True, max_length=255, null=True, verbose_name='Короткое название')),
            ],
            options={
                'abstract': False,
            },
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
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages_received', to=settings.AUTH_USER_MODEL, verbose_name='Получатель')),
            ],
            options={
                'abstract': False,
            },
            bases=('edu_lnmo.message',),
        ),
        migrations.CreateModel(
            name='UnreadObject',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('obj', models.UUIDField(verbose_name='Объект')),
                ('type', models.CharField(choices=[('MSG', 'Сообщение'), ('MRK', 'Оценка'), ('CRS', 'Курс'), ('ACT', 'Активность'), ('NWS', 'Новость'), ('EDU', 'Обучение'), ('FLE', 'Файл'), ('FRM', 'Форум'), ('TSK', 'Задание'), ('UNK', 'Другое')], default='UNK', max_length=3, verbose_name='Тип объекта')),
                ('created', models.DateTimeField(verbose_name='Время')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Mark',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('value', models.CharField(max_length=255, verbose_name='Значение')),
                ('comment', models.TextField(blank=True, verbose_name='Коментарий')),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='marks', to='edu_lnmo.activity', verbose_name='Активность')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL, verbose_name='Выставитель')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student', to=settings.AUTH_USER_MODEL, verbose_name='Учащийся')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EducationSpecialization',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edu_lnmo.department', verbose_name='Подразделение учебного заведения')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('started', models.DateField(verbose_name='Дата поступления')),
                ('finished', models.DateField(blank=True, null=True, verbose_name='Дата завершения')),
                ('starting_class', models.CharField(max_length=10, verbose_name='Класс поступления')),
                ('finishing_class', models.CharField(blank=True, max_length=10, null=True, verbose_name='Класс завершения')),
                ('specialization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='educations', to='edu_lnmo.educationspecialization', verbose_name='Направление обучения')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='education', to=settings.AUTH_USER_MODEL, verbose_name='Учащийся')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='department',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edu_lnmo.organization'),
        ),
        migrations.CreateModel(
            name='CourseEnrollment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('role', models.CharField(choices=[('t', 'Преподаватель'), ('s', 'Учащийся')], max_length=3)),
                ('finished_on', models.DateTimeField(blank=True, null=True, verbose_name='Завершена')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='edu_lnmo.course', verbose_name='Курс')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='course',
            name='cover',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='course_covers', to='edu_lnmo.file', verbose_name='Обложка'),
        ),
        migrations.AddField(
            model_name='course',
            name='for_specialization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='courses', to='edu_lnmo.educationspecialization', verbose_name='Направление обучения'),
        ),
        migrations.AddField(
            model_name='course',
            name='logo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='course_logos', to='edu_lnmo.file', verbose_name='Логотип'),
        ),
        migrations.AddField(
            model_name='activity',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='edu_lnmo.course', verbose_name='Курс'),
        ),
        migrations.AddField(
            model_name='activity',
            name='files',
            field=models.ManyToManyField(blank=True, related_name='activities', to='edu_lnmo.file', verbose_name='Вложения/файлы'),
        ),
        migrations.AddField(
            model_name='activity',
            name='linked_activity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='edu_lnmo.activity'),
        ),
        migrations.CreateModel(
            name='MessageTaskSubmission',
            fields=[
                ('messageprivate_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='edu_lnmo.messageprivate')),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='edu_lnmo.activity', verbose_name='Задание')),
            ],
            options={
                'abstract': False,
            },
            bases=('edu_lnmo.messageprivate',),
        ),
    ]
