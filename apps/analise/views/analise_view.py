from datetime import date

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.ordem_servico.models import OrdemServico
from apps.servicos.models import Servico
from apps.servicos.models.servico import StatusServico
from apps.tarefas.models import Tarefa, MiniOS
from apps.tarefas.models.tarefa import StatusTarefa


class AnaliseDadosView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Análise de dados',
        description=(
            'Métricas agregadas dos últimos 12 meses: ordens de serviço, '
            'serviços, tarefas, mini OS e clientes.'
        ),
    )
    def get(self, request):
        hoje = timezone.now().date()
        meses = _gerar_intervalo_meses(hoje, 12)
        data_inicio = date(meses[0]['ano'], meses[0]['mes'], 1)

        return Response({
            'ordens_servico': self._ordens_servico(data_inicio, meses),
            'servicos': self._servicos(data_inicio, meses),
            'tarefas': self._tarefas(data_inicio, meses),
            'minios': self._minios(data_inicio, meses),
            'clientes': self._clientes(),
        })

    # ------------------------------------------------------------------ #

    def _ordens_servico(self, data_inicio, meses):
        qs = OrdemServico.objects.all()
        vendas_map = _agregar_por_mes(
            qs.filter(data_criacao__gte=data_inicio),
            campo_data='data_criacao',
            agregacao=Sum('valor'),
        )
        return {
            'total': qs.count(),
            'total_concluidas': qs.filter(concluida=True).count(),
            'total_nao_concluidas': qs.filter(concluida=False).count(),
            'vendas_por_mes': _preencher_meses(meses, vendas_map, default=0),
        }

    def _servicos(self, data_inicio, meses):
        concluidos = Servico.objects.filter(
            status=StatusServico.CONCLUIDA,
            data_termino__isnull=False,
            data_termino__gte=data_inicio,
        )
        por_mes_map = _agregar_por_mes(concluidos, campo_data='data_termino')
        principais = list(
            Servico.objects
            .filter(repositorio__isnull=False)
            .values('repositorio_id', 'repositorio__nome')
            .annotate(total=Count('id'))
            .order_by('-total')[:5]
        )
        por_status = [
            {
                'status': item['status'],
                'status_display': dict(StatusServico.choices).get(item['status'], item['status']),
                'total': item['total'],
            }
            for item in Servico.objects.values('status').annotate(total=Count('id'))
        ]
        return {
            'concluidos_ultimos_12_meses_total': concluidos.count(),
            'concluidos_por_mes': _preencher_meses(meses, por_mes_map),
            'principais_por_quantidade': [
                {
                    'repositorio_id': i['repositorio_id'],
                    'repositorio_nome': i['repositorio__nome'],
                    'total': i['total'],
                }
                for i in principais
            ],
            'por_status': por_status,
        }

    def _tarefas(self, data_inicio, meses):
        concluidas = Tarefa.objects.filter(
            status=StatusTarefa.CONCLUIDA,
            data_termino__isnull=False,
            data_termino__gte=data_inicio,
        )
        por_mes_map = _agregar_por_mes(concluidas, campo_data='data_termino')
        por_status = [
            {
                'status': item['status'],
                'status_display': dict(StatusTarefa.choices).get(item['status'], item['status']),
                'total': item['total'],
            }
            for item in Tarefa.objects.values('status').annotate(total=Count('id'))
        ]
        return {
            'por_status': por_status,
            'concluidas_por_mes': _preencher_meses(meses, por_mes_map),
        }

    def _minios(self, data_inicio, meses):
        concluidos = MiniOS.objects.filter(
            status='finalizada',
            data_termino__isnull=False,
            data_termino__gte=data_inicio,
        )
        por_mes_map = _agregar_por_mes(concluidos, campo_data='data_termino')
        qs = MiniOS.objects.all()
        return {
            'total': qs.count(),
            'total_revisao_cliente': qs.filter(revisao_cliente=True).count(),
            'concluidas_ultimos_12_meses_total': concluidos.count(),
            'concluidas_por_mes': _preencher_meses(meses, por_mes_map),
        }

    def _clientes(self):
        mais_faturamento = [
            {
                'cliente_id': i['cliente_id'],
                'cliente_nome': i['cliente__nome'],
                'total_valor_faturado': i['total'] or 0,
            }
            for i in (
                OrdemServico.objects.filter(faturada=True)
                .values('cliente_id', 'cliente__nome')
                .annotate(total=Sum('valor'))
                .order_by('-total')[:5]
            )
            if i['cliente_id'] is not None
        ]
        mais_vendas = [
            {
                'cliente_id': i['cliente_id'],
                'cliente_nome': i['cliente__nome'],
                'total_valor_vendas': i['total'] or 0,
            }
            for i in (
                OrdemServico.objects
                .values('cliente_id', 'cliente__nome')
                .annotate(total=Sum('valor'))
                .order_by('-total')[:10]
            )
            if i['cliente_id'] is not None
        ]
        return {'mais_faturamento': mais_faturamento, 'mais_vendas': mais_vendas}


# ------------------------------------------------------------------ #
# Helpers compartilhados
# ------------------------------------------------------------------ #

def _gerar_intervalo_meses(data_base: date, quantidade: int) -> list:
    meses, ano, mes = [], data_base.year, data_base.month
    for _ in range(quantidade):
        meses.append({'ano': ano, 'mes': mes})
        mes -= 1
        if mes == 0:
            mes, ano = 12, ano - 1
    return list(reversed(meses))


def _agregar_por_mes(queryset, campo_data: str, agregacao=None) -> dict:
    if agregacao is None:
        agregacao = Count('id')
    return {
        item['mes']: item['total']
        for item in (
            queryset
            .annotate(mes=TruncMonth(campo_data))
            .values('mes')
            .annotate(total=agregacao)
        )
    }


def _preencher_meses(meses: list, mapa: dict, default=0) -> list:
    return [
        {
            'ano': m['ano'],
            'mes': m['mes'],
            'total': mapa.get(date(m['ano'], m['mes'], 1), default),
        }
        for m in meses
    ]
