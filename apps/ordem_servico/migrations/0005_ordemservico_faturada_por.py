import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def popular_faturada_por(apps, schema_editor):
    OrdemServico = apps.get_model('ordem_servico', 'OrdemServico')
    Usuario = apps.get_model('contas', 'Usuario')

    if Usuario.objects.filter(pk=3).exists():
        OrdemServico.objects.filter(faturada=True, faturada_por__isnull=True).update(
            faturada_por_id=3
        )


class Migration(migrations.Migration):

    dependencies = [
        ('ordem_servico', '0004_alter_ordemservico_quantidade_parcelas'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='ordemservico',
            name='faturada_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordens_faturadas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(popular_faturada_por, migrations.RunPython.noop),
    ]
