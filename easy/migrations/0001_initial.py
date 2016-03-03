# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.auth.models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer', models.CharField(max_length=30, null=True)),
                ('letter', models.CharField(max_length=1, choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D')])),
                ('image', models.ImageField(upload_to=b'')),
            ],
        ),
        migrations.CreateModel(
            name='ClassLevel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level_name', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'class_levels',
            },
        ),
        migrations.CreateModel(
            name='Director',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'directors',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('exam_name', models.CharField(max_length=30)),
                ('date_available', models.DateTimeField(default=django.utils.timezone.now)),
                ('hours', models.PositiveSmallIntegerField(choices=[(1, b'1 Hour'), (2, b'2 Hours'), (3, b'3 Hours')])),
                ('minutes', models.PositiveSmallIntegerField(choices=[(15, b'15 Minutes'), (30, b'30 Minutes'), (45, b'45 Minutes')])),
                ('class_level', models.ForeignKey(to='easy.ClassLevel')),
            ],
            options={
                'db_table': 'exams',
            },
        ),
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('phone', models.CharField(max_length=13)),
            ],
            options={
                'db_table': 'parents',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.TextField(max_length=200)),
                ('level', models.CharField(max_length=1, null=True, choices=[(b'E', b'Easy'), (b'M', b'Medium'), (b'H', b'Hard')])),
            ],
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('total_marks', models.PositiveSmallIntegerField()),
                ('exam_name', models.ForeignKey(to='easy.Exam')),
            ],
            options={
                'db_table': 'results',
            },
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('school_name', models.CharField(max_length=50)),
                ('mission', models.TextField(max_length=200)),
                ('vision', models.TextField(max_length=200)),
                ('code', models.CharField(max_length=8)),
                ('telephone', models.CharField(max_length=20)),
                ('mobile', models.CharField(max_length=13)),
                ('logo', models.ImageField(null=True, upload_to=b'', blank=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('website', models.URLField(null=True)),
                ('country', models.CharField(default=b'Kenya', max_length=50)),
                ('county', models.CharField(max_length=50, null=True)),
                ('city', models.CharField(max_length=50)),
                ('location', models.CharField(max_length=50, null=True)),
                ('description', models.TextField(max_length=500, null=True)),
                ('gender_type', models.CharField(max_length=1, choices=[(b'B', b"Boy's School"), (b'G', b"Girl's School"), (b'M', b'Mixed')])),
                ('private', models.CharField(max_length=7, choices=[(b'Private', b'Private'), (b'Public', b'Public')])),
                ('approved', models.BooleanField(default=False)),
                ('credit', models.PositiveIntegerField(default=0)),
                ('kindergarten', models.BooleanField(default=False)),
                ('no_of_students', models.PositiveIntegerField(null=True, blank=True)),
                ('app_level', models.CharField(max_length=1, choices=[(b'G', b'Gold'), (b'S', b'Silver'), (b'T', b'Titanium')])),
                ('payed_status', models.BooleanField()),
                ('directors', models.ManyToManyField(to='easy.Director', blank=True)),
            ],
            options={
                'db_table': 'schools',
            },
        ),
        migrations.CreateModel(
            name='SchoolLevel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level_name', models.CharField(max_length=20)),
                ('class_level', models.ManyToManyField(to='easy.ClassLevel')),
            ],
            options={
                'db_table': 'school_levels',
            },
        ),
        migrations.CreateModel(
            name='Stream',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stream_name', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'streams',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('reg_number', models.CharField(max_length=30)),
                ('phone', models.CharField(max_length=13)),
                ('parents', models.ManyToManyField(to='easy.Parent')),
                ('school', models.ForeignKey(to='easy.School')),
                ('stream', models.ForeignKey(to='easy.Stream')),
            ],
            options={
                'db_table': 'students',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject_name', models.CharField(max_length=20)),
                ('class_level', models.ForeignKey(db_column=b'level_name', to='easy.ClassLevel', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('photo', models.ImageField(null=True, upload_to=b'', blank=True)),
                ('phone', models.CharField(max_length=13, null=True)),
                ('gender', models.CharField(max_length=1, null=True, choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('linkdin', models.URLField(null=True)),
                ('position', models.CharField(blank=True, max_length=4, null=True, choices=[(b'HM', b'Head Teacher'), (b'DP', b'Deputy teacher'), (b'SM', b'Senior Master'), (b'EH', b'Examination Head'), (b'AA', b'Academic Affairs'), (b'HOS', b'Head of Sciences'), (b'HOH', b'Head of Humanities'), (b'HOL', b'Head of Languages'), (b'HOM', b'Head of Mathematics')])),
                ('school', models.ForeignKey(related_name='staff', db_column=b'school_name', blank=True, to='easy.School', null=True)),
                ('subjects', models.ManyToManyField(to='easy.Subject', blank=True)),
            ],
            options={
                'db_table': 'teachers',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('topic_name', models.CharField(max_length=50)),
                ('class_level', models.ForeignKey(db_column=b'level_name', to='easy.ClassLevel', null=True)),
                ('subjects', models.ForeignKey(to='easy.Subject', null=True)),
            ],
            options={
                'db_table': 'topics',
            },
        ),
        migrations.CreateModel(
            name='MultipleChoiceQeustion',
            fields=[
                ('question_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='easy.Question')),
                ('choices', models.ManyToManyField(to='easy.Answer', blank=True)),
            ],
            bases=('easy.question',),
        ),
        migrations.AddField(
            model_name='subject',
            name='topics',
            field=models.ManyToManyField(to='easy.Topic', blank=True),
        ),
        migrations.AddField(
            model_name='stream',
            name='class_teacher',
            field=models.ForeignKey(to='easy.Teacher', null=True),
        ),
        migrations.AddField(
            model_name='stream',
            name='level_name',
            field=models.ForeignKey(to='easy.ClassLevel'),
        ),
        migrations.AddField(
            model_name='school',
            name='head',
            field=models.ForeignKey(related_name='skull', to='easy.Teacher', null=True),
        ),
        migrations.AddField(
            model_name='school',
            name='level',
            field=models.ForeignKey(blank=True, to='easy.SchoolLevel', null=True),
        ),
        migrations.AddField(
            model_name='school',
            name='stream',
            field=models.ManyToManyField(to='easy.Stream', blank=True),
        ),
        migrations.AddField(
            model_name='school',
            name='subjects',
            field=models.ManyToManyField(to='easy.Subject', blank=True),
        ),
        migrations.AddField(
            model_name='results',
            name='student_id',
            field=models.ForeignKey(to='easy.Student'),
        ),
        migrations.AddField(
            model_name='question',
            name='class_level',
            field=models.ForeignKey(to='easy.ClassLevel'),
        ),
        migrations.AddField(
            model_name='question',
            name='correct_answer',
            field=models.ForeignKey(to='easy.Answer'),
        ),
        migrations.AddField(
            model_name='question',
            name='question_subject',
            field=models.ForeignKey(to='easy.Subject'),
        ),
        migrations.AddField(
            model_name='question',
            name='question_topic',
            field=models.ForeignKey(to='easy.Topic', null=True),
        ),
        migrations.AddField(
            model_name='exam',
            name='exam_subject',
            field=models.ForeignKey(to='easy.Subject'),
        ),
        migrations.AddField(
            model_name='exam',
            name='supervisor',
            field=models.ForeignKey(to='easy.Teacher'),
        ),
        migrations.AddField(
            model_name='classlevel',
            name='subjects',
            field=models.ManyToManyField(to='easy.Subject', blank=True),
        ),
        migrations.AddField(
            model_name='exam',
            name='questions_ans',
            field=models.ManyToManyField(to='easy.MultipleChoiceQeustion', blank=True),
        ),
    ]
