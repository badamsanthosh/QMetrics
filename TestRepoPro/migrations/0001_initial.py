# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='BugSummary',
            fields=[
                ('bug_id', models.CharField(max_length=15, serialize=False, primary_key=True)),
                ('summary', models.CharField(max_length=255)),
                ('issue_type', models.CharField(max_length=15)),
                ('status', models.CharField(max_length=15)),
                ('components', models.CharField(max_length=100, null=True, blank=True)),
                ('urgency', models.CharField(max_length=20, null=True, blank=True)),
                ('priority', models.CharField(max_length=20, null=True, blank=True)),
                ('assignee', models.CharField(max_length=75, null=True, blank=True)),
                ('qe', models.CharField(max_length=75, null=True, blank=True)),
                ('fix_versions', models.CharField(max_length=100, null=True, blank=True)),
                ('environment', models.CharField(max_length=25, null=True, blank=True)),
                ('sys_env', models.CharField(max_length=25, null=True, blank=True)),
                ('reporter', models.CharField(max_length=75, null=True, blank=True)),
            ],
            options={
                'db_table': 'bug_summary',
            },
        ),
        migrations.CreateModel(
            name='Projects',
            fields=[
                ('pid', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('project_name', models.CharField(unique=True, max_length=30)),
                ('staging_tp', models.CharField(max_length=25)),
                ('stag_tpid', models.CharField(max_length=25)),
                ('production_tp', models.CharField(max_length=25)),
                ('prod_tpid', models.CharField(max_length=25)),
            ],
            options={
                'db_table': 'projects',
            },
        ),
        migrations.CreateModel(
            name='ProjectStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tp_mode', models.CharField(max_length=50)),
                ('build_id', models.CharField(max_length=75, null=True, blank=True)),
                ('tc_count', models.IntegerField(null=True, blank=True)),
                ('tc_pass_count', models.IntegerField(null=True, blank=True)),
                ('tc_fail_count', models.IntegerField(null=True, blank=True)),
                ('tc_nr_count', models.IntegerField(null=True, blank=True)),
                ('tc_block_count', models.IntegerField(null=True, blank=True)),
                ('pid', models.ForeignKey(to='TestRepoPro.Projects', db_column=b'pid')),
            ],
            options={
                'db_table': 'project_stats',
            },
        ),
        migrations.CreateModel(
            name='SecurityOpenPortServices',
            fields=[
                ('ops_id', models.AutoField(serialize=False, primary_key=True)),
                ('port_num', models.IntegerField()),
                ('proto', models.CharField(max_length=20)),
                ('service_name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'sec_open_ports_services',
            },
        ),
        migrations.CreateModel(
            name='SecurityTestExecInfo',
            fields=[
                ('st_id', models.AutoField(serialize=False, primary_key=True)),
                ('exec_id', models.CharField(max_length=125)),
                ('host_name', models.CharField(max_length=25)),
                ('scan_type', models.CharField(max_length=75)),
                ('scan_name', models.CharField(max_length=75)),
                ('critical', models.IntegerField(default=0)),
                ('high', models.IntegerField(default=0)),
                ('medium', models.IntegerField(default=0)),
                ('low', models.IntegerField(default=0)),
                ('info', models.IntegerField(default=0)),
                ('exec_ts', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'sec_test_exec',
            },
        ),
        migrations.CreateModel(
            name='SecurityVulInfo',
            fields=[
                ('vul_id', models.AutoField(serialize=False, primary_key=True)),
                ('severity', models.CharField(max_length=25)),
                ('family', models.CharField(max_length=125)),
                ('name', models.CharField(max_length=255)),
                ('vul_index', models.IntegerField()),
                ('severity_index', models.IntegerField()),
                ('count', models.IntegerField()),
                ('plugin_id', models.IntegerField()),
                ('st_id', models.ForeignKey(to='TestRepoPro.SecurityTestExecInfo', db_column=b'st_id')),
            ],
            options={
                'db_table': 'sec_vul_info',
            },
        ),
        migrations.CreateModel(
            name='TestCases',
            fields=[
                ('tc_id', models.CharField(max_length=15, serialize=False, primary_key=True)),
                ('testcase_name', models.CharField(max_length=75)),
            ],
            options={
                'db_table': 'testcases',
            },
        ),
        migrations.CreateModel(
            name='TestCaseStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tp_mode', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=1)),
                ('exec_time', models.CharField(max_length=30)),
                ('message', models.CharField(max_length=255, null=True, blank=True)),
                ('bug_id', models.CharField(max_length=10, null=True, blank=True)),
                ('tc_id', models.ForeignKey(to='TestRepoPro.TestCases', db_column=b'tc_id')),
            ],
            options={
                'db_table': 'testcase_stats',
            },
        ),
        migrations.CreateModel(
            name='UseCases',
            fields=[
                ('uc_id', models.CharField(max_length=15, serialize=False, primary_key=True)),
                ('usecase_name', models.CharField(max_length=50)),
                ('pid', models.ForeignKey(to='TestRepoPro.Projects', db_column=b'pid')),
            ],
            options={
                'db_table': 'usecases',
            },
        ),
        migrations.CreateModel(
            name='UseCaseStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tp_mode', models.CharField(max_length=50)),
                ('tc_count', models.IntegerField(null=True, blank=True)),
                ('tc_passed', models.IntegerField(null=True, blank=True)),
                ('tc_failed', models.IntegerField(null=True, blank=True)),
                ('tc_not_run', models.IntegerField(null=True, blank=True)),
                ('tc_blocked', models.IntegerField(null=True, blank=True)),
                ('uc_id', models.ForeignKey(to='TestRepoPro.UseCases', db_column=b'uc_id')),
            ],
            options={
                'db_table': 'usecase_stats',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(max_length=25)),
                ('last_name', models.CharField(max_length=25)),
                ('email', models.EmailField(unique=True, max_length=25, verbose_name=b'email address', db_index=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date joined')),
                ('is_staff', models.BooleanField(default=False, help_text=b'Determines if user can access the admin site', verbose_name=b'staff status')),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=True)),
                ('role', models.CharField(max_length=25)),
                ('mgr_id', models.CharField(max_length=10)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.AddField(
            model_name='testcases',
            name='uc_id',
            field=models.ForeignKey(to='TestRepoPro.UseCases', db_column=b'uc_id'),
        ),
        migrations.AddField(
            model_name='securityopenportservices',
            name='st_id',
            field=models.ForeignKey(to='TestRepoPro.SecurityTestExecInfo', db_column=b'st_id'),
        ),
        migrations.AddField(
            model_name='projects',
            name='userid',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, db_column=b'userid'),
        ),
    ]
