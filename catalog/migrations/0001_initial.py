# Generated by Django 3.1.4 on 2020-12-09 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MyModelName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('my_field_name', models.CharField(help_text='Enter field documentation', max_length=20)),
            ],
        ),
    ]