from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.analise.serializers import FinanceiroKPIsSerializer
from apps.contas.permissions import PodeVerValoresFinanceiros
from apps.ordens_servico.models import OrdemServico


class FinanceiroKPIsView(APIView):
    permission_classes = [IsAuthenticated, PodeVerValoresFinanceiros]

    @extend_schema(
        summary='KPIs financeiros',
        description=(
            'Retorna três totalizadores:\n'
            '- **total_cobrado**: soma das OS com cobrança já realizada.\n'
            '- **total_para_cobrar**: soma das OS liberadas e ainda não cobradas.\n'
            '- **total_sem_liberacao**: soma das OS em aberto sem liberação para cobrança.\n\n'
            'Indisponível (403) para os perfis Sub-Líder Técnico, Técnico, '
            'Gestor Administrativo e Administrativo.'
        ),
        responses={
            200: FinanceiroKPIsSerializer,
            403: OpenApiResponse(description='Sem permissão para ver valores financeiros.'),
        },
    )
    def get(self, request):
        qs = OrdemServico.objects.all()

        liberadas = qs.filter(cobranca_realizada=False, liberada_para_cobranca=True)

        total_cobrado = (
            qs.filter(cobranca_realizada=True).aggregate(total=Sum('valor'))['total'] or 0
        )
        total_para_cobrar = (
            liberadas.aggregate(total=Sum('valor'))['total'] or 0
        )
        total_sem_liberacao = (
            qs.filter(cobranca_realizada=False)
            .exclude(pk__in=liberadas.values('pk'))
            .aggregate(total=Sum('valor'))['total'] or 0
        )

        return Response({
            'total_cobrado': total_cobrado,
            'total_para_cobrar': total_para_cobrar,
            'total_sem_liberacao': total_sem_liberacao,
        })
