# Generated by Django 4.0.2 on 2022-02-24 20:28

import VMS.validations
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('VMS', '0003_alter_driver_base_location_alter_driver_branch_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehicle',
            old_name='documents',
            new_name='owner_name',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='maintainence',
        ),
        migrations.AddField(
            model_name='vehiclemaintainance',
            name='vehicle_number',
            field=models.CharField(default='', max_length=30, validators=[VMS.validations.vehicleNumber]),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='number_plate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VMS.vehiclemaintainance'),
        ),
    ]
