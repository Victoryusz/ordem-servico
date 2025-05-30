# Generated by Django 5.2 on 2025-05-06 21:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_order", "0005_alter_ordemservico_descricao_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="stage",
            name="tecnico",
            field=models.ForeignKey(
                blank=True,
                help_text="Técnico responsável pela etapa (fica vazio se excluído).",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
