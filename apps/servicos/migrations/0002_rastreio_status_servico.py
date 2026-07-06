from datetime import datetime, time

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils import timezone


def _as_datetime(value):
    if value is None:
        return None
    return timezone.make_aware(datetime.combine(value, time.min))


def popular_rastreio_servico(apps, schema_editor):
    Servico = apps.get_model('servicos', 'Servico')
    Tarefa = apps.get_model('tarefas', 'Tarefa')
    agora = timezone.now()

    for servico in Servico.objects.select_related('ordem_servico').all().iterator():
        tarefas = Tarefa.objects.filter(servico_id=servico.pk)
        tem_tarefas = tarefas.exists()
        primeira_data_inicio = (
            tarefas
            .filter(data_inicio__isnull=False)
            .order_by('data_inicio', 'id')
            .values_list('data_inicio', flat=True)
            .first()
        )
        ultima_tarefa_concluida = (
            tarefas
            .filter(status='concluida')
            .order_by('-data_termino', '-atualizado_em', '-id')
            .first()
        )
        todos_concluidos = tem_tarefas and not tarefas.exclude(status='concluida').exists()
        tem_execucao = tarefas.filter(status__in=['em_andamento', 'concluida']).exists()

        if servico.status == 'cancelado':
            novo_status = 'cancelado'
        elif todos_concluidos:
            novo_status = 'concluida'
        elif tem_execucao:
            novo_status = 'em_andamento'
        else:
            novo_status = 'aberto'

        data_termino = None
        terminado_por_id = None
        if novo_status == 'concluida':
            data_termino = (
                servico.data_conclusao
                or (ultima_tarefa_concluida.data_termino if ultima_tarefa_concluida else None)
            )
            terminado_por_id = (
                ultima_tarefa_concluida.responsavel_id
                if ultima_tarefa_concluida
                else None
            )

        criado_em = (
            _as_datetime(primeira_data_inicio)
            or _as_datetime(data_termino)
            or _as_datetime(servico.ordem_servico.data_criacao)
            or agora
        )

        Servico.objects.filter(pk=servico.pk).update(
            status=novo_status,
            data_inicio=primeira_data_inicio,
            data_termino=data_termino,
            data_conclusao=data_termino,
            terminado_por_id=terminado_por_id,
            criado_em=criado_em,
            atualizado_em=agora,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('servicos', '0001_initial'),
        ('tarefas', '0002_rastreio_status_tarefa_minios'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='servico',
            name='status',
            field=models.CharField(choices=[('aberto', 'Aberto'), ('em_andamento', 'Em Andamento'), ('concluida', 'Concluído'), ('cancelado', 'Cancelado')], default='aberto', max_length=15),
        ),
        migrations.AddField(
            model_name='servico',
            name='data_inicio',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='servico',
            name='data_termino',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='servico',
            name='terminado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='servicos_terminados', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='servico',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='servico',
            name='atualizado_em',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.RunPython(popular_rastreio_servico, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='servico',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='servico',
            name='atualizado_em',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
