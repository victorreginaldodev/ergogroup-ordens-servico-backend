from datetime import datetime, time

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils import timezone


def _as_datetime(value):
    if value is None:
        return timezone.now()
    return timezone.make_aware(datetime.combine(value, time.min))


def popular_campos_iniciais(apps, schema_editor):
    OrdemServico = apps.get_model('ordem_servico', 'OrdemServico')
    agora = timezone.now()

    for ordem in OrdemServico.objects.all().iterator():
        criada_em = _as_datetime(ordem.data_criacao)
        updates = {
            'criada_em': criada_em,
            'data_atualizacao': agora,
            'status': 'concluida' if ordem.concluida else 'aberta',
            'prioridade': 'baixa',
        }

        if ordem.cobranca_imediata:
            updates.update({
                'liberada_para_faturamento': True,
                'liberada_para_faturamento_em': criada_em,
                'liberada_para_faturamento_por_id': ordem.criado_por_id,
            })

        OrdemServico.objects.filter(pk=ordem.pk).update(**updates)


class Migration(migrations.Migration):

    dependencies = [
        ('ordem_servico', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='ordemservico',
            name='status',
            field=models.CharField(choices=[('aberta', 'Aberta'), ('em_andamento', 'Em Andamento'), ('concluida', 'Concluída'), ('cancelada', 'Cancelada')], default='aberta', max_length=15),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='prioridade',
            field=models.CharField(choices=[('baixa', 'Baixa'), ('media', 'Média'), ('alta', 'Alta')], default='baixa', max_length=10),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='liberada_para_faturamento',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='liberada_para_faturamento_em',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='liberada_para_faturamento_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordens_liberadas_para_faturamento', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='criada_em',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='atualizado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordens_atualizadas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(popular_campos_iniciais, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='ordemservico',
            name='criada_em',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
