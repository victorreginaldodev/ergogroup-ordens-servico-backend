from rest_framework import serializers

from .shared import MesDecimalSerializer


class ClienteCobrancaSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField()
    cliente_nome = serializers.CharField()
    total_valor_cobrado = serializers.DecimalField(max_digits=14, decimal_places=2)


class ClienteVendasSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField()
    cliente_nome = serializers.CharField()
    total_valor_vendas = serializers.DecimalField(max_digits=14, decimal_places=2)


class ClientesAnaliseSerializer(serializers.Serializer):
    mais_cobranca = ClienteCobrancaSerializer(many=True)
    mais_vendas = ClienteVendasSerializer(many=True)


class FinanceiroAnaliseResponseSerializer(serializers.Serializer):
    total_cobrado = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_para_cobrar = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_sem_liberacao = serializers.DecimalField(max_digits=14, decimal_places=2)
    ticket_medio = serializers.DecimalField(max_digits=14, decimal_places=2, allow_null=True)
    vendas_por_mes = MesDecimalSerializer(many=True)
    clientes = ClientesAnaliseSerializer()
