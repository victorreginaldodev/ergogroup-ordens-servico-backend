from datetime import datetime, time

from django.db import migrations
from django.utils import timezone


def _as_datetime(value):
    if value is None:
        return timezone.now()
    return timezone.make_aware(datetime.combine(value, time.min))


def popular_status_liberacao(apps, schema_editor):
    OrdemServico = apps.get_model('ordem_servico', 'OrdemServico')
    Servico = apps.get_model('servicos', 'Servico')
    agora = timezone.now()

    for ordem in OrdemServico.objects.all().iterator():
        servicos = Servico.objects.filter(ordem_servico_id=ordem.pk)
        tem_servicos = servicos.exists()
        todos_concluidos = tem_servicos and not servicos.exclude(status='concluida').exists()
        tem_execucao = servicos.filter(status__in=['em_andamento', 'concluida']).exists()

        if ordem.status == 'cancelada':
            novo_status = 'cancelada'
        elif todos_concluidos:
            novo_status = 'concluida'
        elif tem_execucao:
            novo_status = 'em_andamento'
        else:
            novo_status = 'aberta'

        updates = {
            'status': novo_status,
            'concluida': novo_status == 'concluida',
            'data_atualizacao': agora,
        }

        if not ordem.liberada_para_faturamento:
            if ordem.cobranca_imediata:
                updates.update({
                    'liberada_para_faturamento': True,
                    'liberada_para_faturamento_em': ordem.criada_em or _as_datetime(ordem.data_criacao),
                    'liberada_para_faturamento_por_id': ordem.criado_por_id,
                })
            elif novo_status == 'concluida':
                ultimo_servico = (
                    servicos
                    .filter(status='concluida')
                    .order_by('-data_termino', '-data_conclusao', '-id')
                    .first()
                )
                if ultimo_servico:
                    data_liberacao = ultimo_servico.data_termino or ultimo_servico.data_conclusao
                    updates.update({
                        'liberada_para_faturamento': True,
                        'liberada_para_faturamento_em': _as_datetime(data_liberacao),
                        'liberada_para_faturamento_por_id': ultimo_servico.terminado_por_id,
                    })

        OrdemServico.objects.filter(pk=ordem.pk).update(**updates)


class Migration(migrations.Migration):

    dependencies = [
        ('ordem_servico', '0002_ordemservico_status_prioridade_rastreio_cobranca'),
        ('servicos', '0002_rastreio_status_servico'),
    ]

    operations = [
        migrations.RunPython(popular_status_liberacao, migrations.RunPython.noop),
    ]
