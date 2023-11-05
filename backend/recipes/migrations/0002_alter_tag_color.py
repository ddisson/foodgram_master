# Generated by Django 3.2.3 on 2023-11-04 15:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(default='#49B64E', max_length=7, unique=True, validators=[django.core.validators.RegexValidator('^#[a-fA-F0-9]{6}$', 'Enter a valid HEX color. (e.g., "#FF0033")')], verbose_name='Цвет(HEX)'),
        ),
    ]