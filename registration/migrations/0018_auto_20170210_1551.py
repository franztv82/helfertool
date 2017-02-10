# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-10 14:51
from __future__ import unicode_literals

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0017_event_shirt_sizes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='shirt_sizes',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('S_GIRLY', 'S (girly)'), ('M_GIRLY', 'M (girly)'), ('L_GIRLY', 'L (girly)'), ('XL_GIRLY', 'XL (girly)')], default=('S', 'M', 'L', 'XL', 'XXL', 'S_GIRLY', 'M_GIRLY', 'L_GIRLY', 'XL_GIRLY'), max_length=45, verbose_name='Available T-shirt sizes'),
        ),
    ]
