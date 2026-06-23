from datetime import datetime, time

from django.db import migrations, models
from django.utils import timezone


def _as_datetime(value):
    if value is None:
        return None
    return timezone.make_aware(datetime.combine(value, time.min))


def popular_rastreio(apps, schema_editor):
    Tarefa = apps.get_model('tarefas', 'Tarefa')
    MiniOS = apps.get_model('tarefas', 'MiniOS')
    agora = timezone.now()

    Tarefa.objects.filter(status='nao_iniciada').update(status='aberta')

    for tarefa in Tarefa.objects.select_related('servico__ordem_servico').all().iterator():
        data_base = (
            _as_datetime(tarefa.data_inicio)
            or _as_datetime(tarefa.data_termino)
            or _as_datetime(tarefa.servico.ordem_servico.data_criacao)
            or agora
        )
        Tarefa.objects.filter(pk=tarefa.pk).update(criada_em=data_base)

    for mini_os in MiniOS.objects.all().iterator():
        data_base = (
            _as_datetime(mini_os.data_recebimento)
            or _as_datetime(mini_os.data_inicio)
            or _as_datetime(mini_os.data_termino)
            or agora
        )
        MiniOS.objects.filter(pk=mini_os.pk).update(
            criada_em=data_base,
            atualizado_em=agora,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('tarefas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tarefa',
            name='status',
            field=models.CharField(choices=[('aberta', 'Aberta'), ('em_andamento', 'Em Andamento'), ('concluida', 'Concluída'), ('cancelada', 'Cancelada')], default='aberta', max_length=15),
        ),
        migrations.AddField(
            model_name='tarefa',
            name='criada_em',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='minios',
            name='criada_em',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='minios',
            name='atualizado_em',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.RunPython(popular_rastreio, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='tarefa',
            name='criada_em',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='minios',
            name='criada_em',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='minios',
            name='atualizado_em',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
