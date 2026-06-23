from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.ordem_servico.models import OrdemServico


class FinanceiroKPIsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='KPIs financeiros',
        description=(
            'Retorna três totalizadores:\n'
            '- **total_faturado**: soma das OS já faturadas.\n'
            '- **total_para_faturar**: soma das OS liberadas e ainda não faturadas.\n'
            '- **total_sem_liberacao**: soma das OS em aberto sem liberação para faturamento.'
        ),
    )
    def get(self, request):
        qs = OrdemServico.objects.all()

        liberadas = qs.filter(faturada=False, liberada_para_faturamento=True)

        total_faturado = (
            qs.filter(faturada=True).aggregate(total=Sum('valor'))['total'] or 0
        )
        total_para_faturar = (
            liberadas.aggregate(total=Sum('valor'))['total'] or 0
        )
        total_sem_liberacao = (
            qs.filter(faturada=False)
            .exclude(pk__in=liberadas.values('pk'))
            .aggregate(total=Sum('valor'))['total'] or 0
        )

        return Response({
            'total_faturado': total_faturado,
            'total_para_faturar': total_para_faturar,
            'total_sem_liberacao': total_sem_liberacao,
        })
