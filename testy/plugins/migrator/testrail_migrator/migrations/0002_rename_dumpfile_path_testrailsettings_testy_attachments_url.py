# Generated by Django 3.2 on 2022-12-20 03:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testrail_migrator', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='testrailsettings',
            old_name='dumpfile_path',
            new_name='testy_attachments_url',
        ),
    ]
