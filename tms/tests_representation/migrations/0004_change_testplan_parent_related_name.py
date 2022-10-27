# Generated by Django 3.2 on 2022-10-21 05:41

from django.db import migrations
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tests_representation', '0003_make_user_nullable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testplan',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_test_plans', to='tests_representation.testplan'),
        ),
    ]
