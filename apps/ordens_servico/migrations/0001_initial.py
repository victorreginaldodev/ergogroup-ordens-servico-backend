import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    # Substitui integralmente o histórico das apps ordem_servico, servicos e
    # tarefas: os models que viviam nelas foram consolidados aqui (e em
    # apps.catalogo). Numa base já migrada, estas 12 migrations já estão
    # aplicadas e esta simplesmente assume o lugar delas sem re-executar nada;
    # numa base nova, cria o estado final diretamente, sem passar pelo
    # esquema antigo (data_criacao/faturada/repositorio_id/etc.).
    replaces = [
        ('ordem_servico', '0001_initial'),
        ('ordem_servico', '0002_ordemservico_status_prioridade_rastreio_cobranca'),
        ('ordem_servico', '0003_popular_status_liberacao_faturamento'),
        ('ordem_servico', '0004_alter_ordemservico_quantidade_parcelas'),
        ('ordem_servico', '0005_ordemservico_faturada_por'),
        ('ordem_servico', '0006_ordemservico_contrato'),
        ('servicos', '0001_initial'),
        ('servicos', '0002_rastreio_status_servico'),
        ('servicos', '0003_subitem_repositorio'),
        ('tarefas', '0001_initial'),
        ('tarefas', '0002_rastreio_status_tarefa_minios'),
        ('tarefas', '0003_minios_cobranca'),
    ]

    dependencies = [
        ('clientes', '0001_initial'),
        ('catalogo', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OrdemServico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_venda', models.DateField()),
                ('concluida', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('aberta', 'Aberta'), ('em_andamento', 'Em Andamento'), ('concluida', 'Concluída'), ('cancelada', 'Cancelada')], default='aberta', max_length=15)),
                ('prioridade', models.CharField(choices=[('baixa', 'Baixa'), ('media', 'Média'), ('alta', 'Alta')], default='baixa', max_length=10)),
                ('valor', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('forma_pagamento', models.CharField(choices=[('pix', 'PIX'), ('credito', 'Crédito'), ('debito', 'Débito'), ('boleto', 'Boleto'), ('transferencia', 'Transferência'), ('dinheiro', 'Dinheiro'), ('cheque', 'Cheque'), ('outro', 'Outro')], default='boleto', max_length=15)),
                ('quantidade_parcelas', models.IntegerField(blank=True, null=True)),
                ('cobranca_imediata', models.BooleanField(default=False)),
                ('data_acordada_cobranca', models.DateField(blank=True, null=True)),
                ('nome_contato_envio_nf', models.CharField(default='', max_length=50)),
                ('contato_envio_nf', models.EmailField(default='', max_length=254)),
                ('observacao', models.TextField(blank=True, null=True)),
                ('contrato', models.BooleanField(default=False)),
                ('objeto_contrato', models.CharField(blank=True, max_length=255, null=True)),
                ('contrato_data_inicio', models.DateField(blank=True, null=True)),
                ('contrato_data_fim', models.DateField(blank=True, null=True)),
                ('gestor_contrato_nome', models.CharField(blank=True, max_length=255, null=True)),
                ('gestor_contrato_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('gestor_contrato_telefone', models.CharField(blank=True, max_length=30, null=True)),
                ('liberada_para_cobranca', models.BooleanField(default=False)),
                ('liberada_para_cobranca_em', models.DateTimeField(blank=True, null=True)),
                ('cobranca_realizada', models.BooleanField(default=False)),
                ('numero_nf', models.IntegerField(blank=True, null=True)),
                ('data_cobranca', models.DateField(blank=True, null=True)),
                ('criada_em', models.DateTimeField(auto_now_add=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ordens_servico', to='clientes.cliente')),
                ('criado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordens_criadas', to=settings.AUTH_USER_MODEL)),
                ('atualizado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordens_atualizadas', to=settings.AUTH_USER_MODEL)),
                ('liberada_para_cobranca_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordens_liberadas_para_cobranca', to=settings.AUTH_USER_MODEL)),
                ('cobranca_realizada_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordens_cobranca_realizada', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Ordem de Serviço',
                'verbose_name_plural': 'Ordens de Serviço',
                'ordering': ['-data_venda'],
            },
        ),
        migrations.CreateModel(
            name='Servico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.TextField()),
                ('status', models.CharField(choices=[('aberto', 'Aberto'), ('em_andamento', 'Em Andamento'), ('concluida', 'Concluído'), ('cancelado', 'Cancelado')], default='aberto', max_length=15)),
                ('data_inicio', models.DateField(blank=True, null=True)),
                ('data_termino', models.DateField(blank=True, null=True)),
                ('data_conclusao', models.DateField(blank=True, null=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('ordem_servico', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='servicos', to='ordens_servico.ordemservico')),
                ('catalogo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='catalogo.catalogo')),
                ('terminado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='servicos_terminados', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Serviço',
                'verbose_name_plural': 'Serviços',
                'ordering': ['ordem_servico', 'status'],
            },
        ),
        migrations.CreateModel(
            name='Tarefa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.TextField(blank=True, null=True)),
                ('data_inicio', models.DateField(blank=True, null=True)),
                ('data_termino', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('aberta', 'Aberta'), ('em_andamento', 'Em Andamento'), ('concluida', 'Concluída'), ('cancelada', 'Cancelada')], default='aberta', max_length=15)),
                ('criada_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('servico', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tarefas', to='ordens_servico.servico')),
                ('responsavel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tarefas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Tarefa',
                'verbose_name_plural': 'Tarefas',
                'ordering': ['servico', 'status'],
            },
        ),
        migrations.CreateModel(
            name='OrdemServicoOperacional',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.PositiveIntegerField(default=1)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('data_recebimento', models.DateField(blank=True, null=True)),
                ('data_inicio', models.DateField(blank=True, null=True)),
                ('data_termino', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('nao_iniciado', 'Não Iniciado'), ('em_andamento', 'Em Andamento'), ('finalizada', 'Finalizada')], default='nao_iniciado', max_length=15)),
                ('criada_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('revisao_cliente', models.BooleanField(default=False)),
                ('gera_cobranca', models.BooleanField(default=False)),
                ('data_liberacao_cobranca', models.DateTimeField(blank=True, null=True)),
                ('cobranca_realizada', models.BooleanField(default=False)),
                ('numero_nf', models.CharField(blank=True, max_length=10, null=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ordens_servico_operacionais', to='clientes.cliente')),
                ('catalogo_operacional', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ordens_servico_operacionais', to='catalogo.catalogooperacional')),
                ('responsavel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordens_servico_operacionais', to=settings.AUTH_USER_MODEL)),
                ('liberada_cobranca_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordens_servico_operacionais_liberadas_cobranca', to=settings.AUTH_USER_MODEL)),
                ('cobranca_realizada_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordens_servico_operacionais_cobranca_realizada', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Ordem de Serviço Operacional',
                'verbose_name_plural': 'Ordens de Serviço Operacionais',
                'ordering': ['-data_recebimento'],
            },
        ),
    ]
