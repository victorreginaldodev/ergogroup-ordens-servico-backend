from django.db.models import Sum, Q, Count, F, OuterRef, Subquery
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from legado.ordemServico.models import OrdemServico, Servico


class FinanceiroKPIsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = OrdemServico.objects.all()

        servicos_concluidos_subquery = (
            Servico.objects.filter(
                ordem_servico=OuterRef('pk'),
                status='concluida',
            )
            .values('ordem_servico')
            .annotate(count=Count('id'))
            .values('count')
        )

        total_servicos_subquery = (
            Servico.objects.filter(
                ordem_servico=OuterRef('pk'),
            )
            .values('ordem_servico')
            .annotate(count=Count('id'))
            .values('count')
        )

        annotated = queryset.annotate(
            total_servicos=Subquery(total_servicos_subquery),
            servicos_concluidos=Subquery(servicos_concluidos_subquery),
        )

        liberadas = (
            annotated.filter(faturamento='nao')
            .filter(
                Q(cobranca_imediata='sim') |
                Q(
                    servicos__isnull=False,
                    total_servicos=F('servicos_concluidos'),
                )
            )
            .distinct()
        )

        total_faturado = (
            queryset.filter(faturamento='sim')
            .aggregate(total=Sum('valor'))
            .get('total')
            or 0
        )

        total_para_faturar = (
            liberadas.aggregate(total=Sum('valor')).get('total') or 0
        )

        total_sem_liberacao = sum(
            ordem.valor
            for ordem in queryset
            if not ordem.liberada_para_faturamento()
        )

        data = {
            'total_faturado': total_faturado,
            'total_para_faturar': total_para_faturar,
            'total_sem_liberacao': total_sem_liberacao,
        }

        return Response(data)


