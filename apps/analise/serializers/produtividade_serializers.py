from rest_framework import serializers

from .shared import MesSerializer


class DistribuicaoTempoOSSerializer(serializers.Serializer):
    ate_7 = serializers.IntegerField()
    de_8_a_15 = serializers.IntegerField()
    de_16_a_30 = serializers.IntegerField()
    de_31_a_60 = serializers.IntegerField()
    acima_60 = serializers.IntegerField()


class TempoPorRepositorioSerializer(serializers.Serializer):
    repositorio_id = serializers.IntegerField()
    repositorio_nome = serializers.CharField()
    total_concluidos = serializers.IntegerField()
    media_dias = serializers.FloatField()


class TemposMediosSerializer(serializers.Serializer):
    os_criacao_para_encerramento_dias = serializers.FloatField(allow_null=True)
    os_criacao_para_conclusao_dias = serializers.FloatField(allow_null=True)
    os_total_com_data = serializers.IntegerField()
    os_distribuicao_tempo = DistribuicaoTempoOSSerializer()
    servicos_inicio_para_fim_dias = serializers.FloatField(allow_null=True)
    tarefa_criacao_para_inicio_dias = serializers.FloatField(allow_null=True)
    tempo_por_repositorio = TempoPorRepositorioSerializer(many=True)


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
    mini_os_concluidas = serializers.IntegerField()
    tarefas_em_aberto = serializers.IntegerField()
    mini_os_em_aberto = serializers.IntegerField()
    tarefas_concluidas_por_mes = MesSerializer(many=True)
    mini_os_concluidas_por_mes = MesSerializer(many=True)


class ProdutividadeResponseSerializer(serializers.Serializer):
    tempos_medios = TemposMediosSerializer()
    taxa_cancelamento = TaxaCancelamentoSerializer()
    por_tecnico = TecnicoProdutividadeSerializer(many=True)
