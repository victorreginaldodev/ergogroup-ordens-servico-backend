from rest_framework import serializers

from .shared import MesSerializer


class DistribuicaoTempoOSSerializer(serializers.Serializer):
    ate_7 = serializers.IntegerField()
    de_8_a_15 = serializers.IntegerField()
    de_16_a_30 = serializers.IntegerField()
    de_31_a_60 = serializers.IntegerField()
    acima_60 = serializers.IntegerField()


class TempoPorCatalogoSerializer(serializers.Serializer):
    catalogo_id = serializers.IntegerField()
    catalogo_nome = serializers.CharField()
    horas_estimadas = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)
    complexidade = serializers.IntegerField(allow_null=True)
    total_concluidos = serializers.IntegerField()
    media_dias = serializers.FloatField()


class TemposMediosSerializer(serializers.Serializer):
    os_criacao_para_encerramento_dias = serializers.FloatField(allow_null=True)
    os_criacao_para_conclusao_dias = serializers.FloatField(allow_null=True)
    os_total_com_data = serializers.IntegerField()
    os_distribuicao_tempo = DistribuicaoTempoOSSerializer()
    servicos_inicio_para_fim_dias = serializers.FloatField(allow_null=True)
    tarefa_criacao_para_inicio_dias = serializers.FloatField(allow_null=True)
    tempo_por_catalogo = TempoPorCatalogoSerializer(many=True)


class BlocoCancelamentoSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    canceladas = serializers.IntegerField()
    percentual = serializers.FloatField(allow_null=True)


class TaxaCancelamentoSerializer(serializers.Serializer):
    tarefas = BlocoCancelamentoSerializer()
    servicos = BlocoCancelamentoSerializer()


class TecnicoProdutividadeSerializer(serializers.Serializer):
    tecnico_id = serializers.IntegerField()
    tecnico_nome = serializers.CharField(allow_null=True)
    tarefas_concluidas = serializers.IntegerField()
    tempo_medio_tarefa_dias = serializers.FloatField(allow_null=True)
    complexidade_media_concluidas = serializers.FloatField(allow_null=True)
    horas_estimadas_entregues = serializers.DecimalField(max_digits=8, decimal_places=2)
    mini_os_concluidas = serializers.IntegerField()
    tarefas_em_aberto = serializers.IntegerField()
    mini_os_em_aberto = serializers.IntegerField()
    tarefas_atrasadas = serializers.IntegerField()
    mini_os_atrasadas = serializers.IntegerField()
    tarefas_alta_prioridade_abertas = serializers.IntegerField()
    mini_os_alta_prioridade_abertas = serializers.IntegerField()
    tarefas_concluidas_por_mes = MesSerializer(many=True)
    mini_os_concluidas_por_mes = MesSerializer(many=True)


class ProdutividadeResponseSerializer(serializers.Serializer):
    tempos_medios = TemposMediosSerializer()
    taxa_cancelamento = TaxaCancelamentoSerializer()
    por_tecnico = TecnicoProdutividadeSerializer(many=True)
