# Generated by Django 5.0.4 on 2024-05-03 19:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('howard_web', '0002_rename_nombres_tipopago_nombre'),
    ]

    operations = [
        migrations.RenameField(
            model_name='horario',
            old_name='tipoturno',
            new_name='tipo_turno',
        ),
    ]