from rest_framework import serializers

from .shared import MesSerializer, MesDecimalSerializer


class ServicoPorStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    status_display = serializers.CharField()
    total = serializers.IntegerField()


class ServicoPrincipalSerializer(serializers.Serializer):
    repositorio_id = serializers.IntegerField()
    repositorio_nome = serializers.CharField()
    total = serializers.IntegerField()


class OrdensServicoAnaliseSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    total_concluidas = serializers.IntegerField()
    total_nao_concluidas = serializers.IntegerField()
    abertas_por_mes = MesSerializer(many=True)
    concluidas_por_mes = MesSerializer(many=True)
    abertas_mes_atual = serializers.IntegerField()
    abertas_mes_anterior = serializers.IntegerField()
    concluidas_mes_atual = serializers.IntegerField()
    concluidas_mes_anterior = serializers.IntegerField()
    em_aberto = serializers.IntegerField()
    vendas_por_mes = MesDecimalSerializer(many=True, required=False)


class ServicoAnaliseSerializer(serializers.Serializer):
    concluidos_ultimos_12_meses_total = serializers.IntegerField()
    concluidos_por_mes = MesSerializer(many=True)
    principais_por_quantidade = ServicoPrincipalSerializer(many=True)
    por_status = ServicoPorStatusSerializer(many=True)


class TarefaPorStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    status_display = serializers.CharField()
    total = serializers.IntegerField()


class TarefaAnaliseSerializer(serializers.Serializer):
    por_status = TarefaPorStatusSerializer(many=True)
    concluidas_por_mes = MesSerializer(many=True)


class RevisaoPorClienteSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField()
    cliente_nome = serializers.CharField()
    total = serializers.IntegerField()


class MiniOSAnaliseSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    total_revisao_cliente = serializers.IntegerField()
    criadas_por_mes = MesSerializer(many=True)
    finalizadas_por_mes = MesSerializer(many=True)
    criadas_mes_atual = serializers.IntegerField()
    criadas_mes_anterior = serializers.IntegerField()
    finalizadas_mes_atual = serializers.IntegerField()
    finalizadas_mes_anterior = serializers.IntegerField()
    revisoes_por_cliente = RevisaoPorClienteSerializer(many=True)


class ClienteFaturamentoSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField()
    cliente_nome = serializers.CharField()
    total_valor_faturado = serializers.DecimalField(max_digits=14, decimal_places=2)


class ClienteVendasSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField()
    cliente_nome = serializers.CharField()
    total_valor_vendas = serializers.DecimalField(max_digits=14, decimal_places=2)


class ClientesAnaliseSerializer(serializers.Serializer):
    mais_faturamento = ClienteFaturamentoSerializer(many=True)
    mais_vendas = ClienteVendasSerializer(many=True)


class AnaliseDadosResponseSerializer(serializers.Serializer):
    ordens_servico = OrdensServicoAnaliseSerializer()
    servicos = ServicoAnaliseSerializer()
    tarefas = TarefaAnaliseSerializer()
    minios = MiniOSAnaliseSerializer()
    clientes = ClientesAnaliseSerializer(required=False)
