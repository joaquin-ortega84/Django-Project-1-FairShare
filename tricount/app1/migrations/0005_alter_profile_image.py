# Generated by Django 4.2.3 on 2023-08-07 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0004_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='default.png', upload_to='profile_pics'),
        ),
    ]
