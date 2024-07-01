# Generated by Django 3.1.7 on 2021-05-29 16:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GroupModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=64)),
                ('email', models.CharField(max_length=64)),
                ('password', models.CharField(max_length=64)),
                ('first_name', models.CharField(max_length=64)),
                ('last_name', models.CharField(max_length=64)),
                ('birthdate', models.DateField()),
                ('job_title', models.CharField(max_length=64)),
                ('company', models.CharField(max_length=64)),
                ('photo', models.ImageField(null=True, upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='TaskModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('execution_date', models.DateField()),
                ('deadline', models.DateField()),
                ('description', models.TextField()),
                ('fruits', models.TextField()),
                ('state', models.TextField()),
                ('personal_date', models.DateField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.usermodel')),
                ('group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.groupmodel')),
            ],
        ),
        migrations.CreateModel(
            name='PingModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ping_type', models.TextField()),
                ('message', models.TextField(null=True)),
                ('date', models.DateTimeField(null=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.taskmodel')),
                ('user_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_from', to='backend.usermodel')),
                ('user_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_to', to='backend.usermodel')),
            ],
        ),
        migrations.CreateModel(
            name='OrganizerModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('personal_date', models.DateField()),
                ('next_organizer', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='backend.organizermodel')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.taskmodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.usermodel')),
            ],
        ),
        migrations.CreateModel(
            name='MembershipModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.groupmodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.usermodel')),
            ],
        ),
        migrations.AddField(
            model_name='groupmodel',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.usermodel'),
        ),
    ]