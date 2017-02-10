# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-10 16:07
from __future__ import unicode_literals

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0018_auto_20170210_1551'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='shirt_sizes',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('NO', 'I do not want a T-Shirt'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('S_GIRLY', 'S (girly)'), ('M_GIRLY', 'M (girly)'), ('L_GIRLY', 'L (girly)'), ('XL_GIRLY', 'XL (girly)')], default=['S', 'M', 'L', 'XL', 'XXL', 'S_GIRLY', 'M_GIRLY', 'L_GIRLY', 'XL_GIRLY'], max_length=48, verbose_name='Available T-shirt sizes'),
        ),
        migrations.AlterField(
            model_name='helper',
            name='shirt',
            field=models.CharField(choices=[('UNKNOWN', 'Unknown'), ('NO', 'I do not want a T-Shirt'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('S_GIRLY', 'S (girly)'), ('M_GIRLY', 'M (girly)'), ('L_GIRLY', 'L (girly)'), ('XL_GIRLY', 'XL (girly)')], default='UNKNOWN', max_length=20, verbose_name='T-shirt'),
        ),
    ]
