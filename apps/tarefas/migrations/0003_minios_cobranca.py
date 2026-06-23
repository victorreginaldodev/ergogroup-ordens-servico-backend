from datetime import datetime, time

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils import timezone


def _as_datetime(value):
    if value is None:
        return None
    return timezone.make_aware(datetime.combine(value, time.min))


def popular_cobranca_minios(apps, schema_editor):
    MiniOS = apps.get_model('tarefas', 'MiniOS')
    Usuario = apps.get_model('contas', 'Usuario')
    usuario_faturamento_id = 3 if Usuario.objects.filter(pk=3).exists() else None
    agora = timezone.now()

    for mini_os in MiniOS.objects.all().iterator():
        gera_cobranca = bool(mini_os.revisao_cliente)
        data_liberacao_cobranca = None
        liberada_cobranca_por_id = None

        if gera_cobranca and mini_os.status == 'finalizada':
            data_liberacao_cobranca = (
                _as_datetime(mini_os.data_termino)
                or mini_os.atualizado_em
                or agora
            )
            liberada_cobranca_por_id = mini_os.responsavel_id

        MiniOS.objects.filter(pk=mini_os.pk).update(
            gera_cobranca=gera_cobranca,
            data_liberacao_cobranca=data_liberacao_cobranca,
            liberada_cobranca_por_id=liberada_cobranca_por_id,
            faturada_por_id=(
                usuario_faturamento_id
                if mini_os.faturada and usuario_faturamento_id
                else None
            ),
        )


class Migration(migrations.Migration):

    dependencies = [
        ('tarefas', '0002_rastreio_status_tarefa_minios'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='minios',
            name='gera_cobranca',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='minios',
            name='data_liberacao_cobranca',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='minios',
            name='liberada_cobranca_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mini_os_liberadas_cobranca', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='minios',
            name='faturada_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mini_os_faturadas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(popular_cobranca_minios, migrations.RunPython.noop),
    ]
