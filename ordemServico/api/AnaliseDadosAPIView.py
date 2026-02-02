from datetime import date, timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ordemServico.models import MiniOS, OrdemServico, Servico, Tarefa


class AnaliseDadosAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limite_periodo = timezone.now() - timedelta(days=365)
        limite_data = limite_periodo.date()
        hoje = timezone.now().date()
        meses = self._gerar_intervalo_meses(hoje, 12)
        data_inicio = date(meses[0]['ano'], meses[0]['mes'], 1)

        ordens_queryset = OrdemServico.objects.all()
        total_ordens = ordens_queryset.count()
        total_concluidas = ordens_queryset.filter(concluida='sim').count()
        total_nao_concluidas = ordens_queryset.filter(concluida='nao').count()

        servicos_concluidos_periodo = Servico.objects.filter(
            status='concluida',
            data_conclusao__isnull=False,
            data_conclusao__gte=data_inicio,
        )
        servicos_concluidos_total = servicos_concluidos_periodo.count()
        servicos_concluidos_por_mes_queryset = (
            servicos_concluidos_periodo.annotate(mes=TruncMonth('data_conclusao'))
            .values('mes')
            .annotate(total=Count('id'))
        )
        contagem_por_mes = {item['mes']: item['total'] for item in servicos_concluidos_por_mes_queryset}
        servicos_concluidos_por_mes = []
        for item_mes in meses:
            chave_mes = date(item_mes['ano'], item_mes['mes'], 1)
            servicos_concluidos_por_mes.append(
                {
                    'ano': item_mes['ano'],
                    'mes': item_mes['mes'],
                    'total': contagem_por_mes.get(chave_mes, 0),
                }
            )

        principais_servicos_queryset = (
            Servico.objects.values('repositorio_id', 'repositorio__nome')
            .annotate(total=Count('id'))
            .order_by('-total')[:5]
        )
        principais_servicos = [
            {
                'repositorio_id': item['repositorio_id'],
                'repositorio_nome': item['repositorio__nome'],
                'total': item['total'],
            }
            for item in principais_servicos_queryset
            if item['repositorio_id'] is not None
        ]

        status_display_map = dict(Servico.STATUS)
        servicos_por_status = [
            {
                'status': item['status'],
                'status_display': status_display_map.get(item['status'], item['status']),
                'total': item['total'],
            }
            for item in Servico.objects.values('status').annotate(total=Count('id'))
        ]

        status_display_map = dict(Tarefa.STATUS)
        tarefas_por_status = [
            {
                'status': item['status'],
                'status_display': status_display_map.get(item['status'], item['status']),
                'total': item['total'],
            }
            for item in Tarefa.objects.values('status').annotate(total=Count('id'))
        ]

        tarefas_concluidas_periodo = Tarefa.objects.filter(
            status='concluida',
            data_termino__isnull=False,
            data_termino__gte=data_inicio,
        )
        tarefas_por_mes_queryset = (
            tarefas_concluidas_periodo.annotate(mes=TruncMonth('data_termino'))
            .values('mes')
            .annotate(total=Count('id'))
        )
        tarefas_por_mes_map = {item['mes']: item['total'] for item in tarefas_por_mes_queryset}
        tarefas_concluidas_por_mes = []
        for item_mes in meses:
            chave_mes = date(item_mes['ano'], item_mes['mes'], 1)
            tarefas_concluidas_por_mes.append(
                {
                    'ano': item_mes['ano'],
                    'mes': item_mes['mes'],
                    'total': tarefas_por_mes_map.get(chave_mes, 0),
                }
            )

        minios_concluidas_periodo = MiniOS.objects.filter(
            status='finalizada',
            data_termino__isnull=False,
            data_termino__gte=data_inicio,
        )
        minios_concluidas_total = minios_concluidas_periodo.count()
        minios_por_mes_queryset = (
            minios_concluidas_periodo.annotate(mes=TruncMonth('data_termino'))
            .values('mes')
            .annotate(total=Count('id'))
        )
        minios_por_mes_map = {item['mes']: item['total'] for item in minios_por_mes_queryset}
        minios_concluidas_por_mes = []
        for item_mes in meses:
            chave_mes = date(item_mes['ano'], item_mes['mes'], 1)
            minios_concluidas_por_mes.append(
                {
                    'ano': item_mes['ano'],
                    'mes': item_mes['mes'],
                    'total': minios_por_mes_map.get(chave_mes, 0),
                }
            )

        minios_queryset = MiniOS.objects.all()
        minios_total = minios_queryset.count()
        minios_revisao_cliente_total = minios_queryset.filter(revisao_cliente=True).count()

        clientes_top_queryset = (
            OrdemServico.objects.filter(faturamento='sim')
            .values('cliente_id', 'cliente__nome')
            .annotate(total=Sum('valor'))
            .order_by('-total')[:5]
        )
        clientes_mais_faturamento = [
            {
                'cliente_id': item['cliente_id'],
                'cliente_nome': item['cliente__nome'],
                'total_valor_faturado': item['total'] or 0,
            }
            for item in clientes_top_queryset
            if item['cliente_id'] is not None
        ]

        vendas_periodo = OrdemServico.objects.filter(
            data_criacao__gte=data_inicio
        )
        vendas_por_mes_queryset = (
            vendas_periodo.annotate(mes=TruncMonth('data_criacao'))
            .values('mes')
            .annotate(total=Sum('valor'))
        )
        vendas_por_mes_map = {item['mes']: item['total'] for item in vendas_por_mes_queryset}
        vendas_por_mes = []
        for item_mes in meses:
            chave_mes = date(item_mes['ano'], item_mes['mes'], 1)
            vendas_por_mes.append(
                {
                    'ano': item_mes['ano'],
                    'mes': item_mes['mes'],
                    'total': vendas_por_mes_map.get(chave_mes, 0) or 0,
                }
            )

        clientes_vendas_queryset = (
            OrdemServico.objects.values('cliente_id', 'cliente__nome')
            .annotate(total=Sum('valor'))
            .order_by('-total')[:10]
        )
        clientes_mais_vendas = [
            {
                'cliente_id': item['cliente_id'],
                'cliente_nome': item['cliente__nome'],
                'total_valor_vendas': item['total'] or 0,
            }
            for item in clientes_vendas_queryset
            if item['cliente_id'] is not None
        ]

        data = {
            'ordens_servico': {
                'total': total_ordens,
                'total_concluidas': total_concluidas,
                'total_nao_concluidas': total_nao_concluidas,
                'vendas_por_mes': vendas_por_mes,
            },
            'servicos': {
                'concluidos_ultimos_12_meses_total': servicos_concluidos_total,
                'concluidos_por_mes': servicos_concluidos_por_mes,
                'principais_por_quantidade': principais_servicos,
                'por_status': servicos_por_status,
            },
            'tarefas': {
                'por_status': tarefas_por_status,
                'concluidas_por_mes': tarefas_concluidas_por_mes,
            },
            'minios': {
                'concluidas_ultimos_12_meses_total': minios_concluidas_total,
                'concluidas_por_mes': minios_concluidas_por_mes,
                'total': minios_total,
                'total_revisao_cliente': minios_revisao_cliente_total,
            },
            'clientes': {
                'mais_faturamento': clientes_mais_faturamento,
                'mais_vendas': clientes_mais_vendas,
            },
        }

        return Response(data)

    @staticmethod
    def _gerar_intervalo_meses(data_base: date, quantidade: int):
        meses = []
        ano = data_base.year
        mes = data_base.month
        for _ in range(quantidade):
            meses.append({'ano': ano, 'mes': mes})
            mes -= 1
            if mes == 0:
                mes = 12
                ano -= 1
        return list(reversed(meses))

