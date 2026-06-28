from rest_framework import serializers


class FinanceiroKPIsSerializer(serializers.Serializer):
    total_faturado = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_para_faturar = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_sem_liberacao = serializers.DecimalField(max_digits=14, decimal_places=2)
