# Generated by Django 3.1.12 on 2021-07-03 13:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crypto', '0003_auto_20210703_1302'),
    ]

    operations = [
        migrations.RenameField(
            model_name='criptoalert',
            old_name='curreny',
            new_name='currency',
        ),
    ]
