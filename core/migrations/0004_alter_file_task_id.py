# Generated by Django 3.2.9 on 2021-12-29 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20211229_1824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='task_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]